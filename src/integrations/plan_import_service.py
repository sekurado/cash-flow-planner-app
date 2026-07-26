from __future__ import annotations

import json
from pathlib import Path

from pydantic import ValidationError
from sqlalchemy.engine import Connection

from src.app.identity import SUPPORTED_IMPORT_APP_IDS
from src.data.repositories.entry_repo import AbstractEntryRepository, EntryCreateDto
from src.data.repositories.exchange_rate_repo import (
    AbstractExchangeRateRepository,
    ExchangeRateUpsertDto,
    SqliteExchangeRateRepository,
)
from src.data.repositories.plan_repo import AbstractPlanRepository, PlanCreateDto
from src.domain.date_pattern import parse_pattern
from src.domain.entities import (
    PlanExportBundle,
    PlanExportRate,
    PlanImportPreview,
    RateConflict,
)
from src.domain.exceptions import DatePatternParseError, PlanImportError

_SUPPORTED_FORMAT_VERSION = 1
_RATE_EPSILON = 1e-6
_IMPORTED_SUFFIX = " (imported)"


class PlanImportService:
    def __init__(
        self,
        plan_repo: AbstractPlanRepository,
        entry_repo: AbstractEntryRepository,
        exchange_rate_repo: AbstractExchangeRateRepository,
        conn: Connection,
    ) -> None:
        self._plan_repo = plan_repo
        self._entry_repo = entry_repo
        self._exchange_rate_repo = exchange_rate_repo
        self._conn = conn

    def inspect(self, path: Path) -> PlanImportPreview:
        bundle = self._load_bundle(path)
        additions, conflicts, unchanged = self._classify_rates(bundle)
        return PlanImportPreview(
            bundle=bundle,
            rate_additions=additions,
            rate_conflicts=conflicts,
            rate_unchanged=unchanged,
        )

    def import_bundle(
        self,
        bundle: PlanExportBundle,
        rate_resolutions: dict[str, str],
    ) -> str:
        self._validate_format_version(bundle.format_version)
        additions, conflicts, _unchanged = self._classify_rates(bundle)
        self._validate_rate_resolutions(conflicts, rate_resolutions)
        self._validate_entry_patterns(bundle)

        plan_name = self._resolve_import_name(bundle.plan.name)

        try:
            with self._conn.begin_nested():
                plan = self._plan_repo.create(
                    PlanCreateDto(
                        name=plan_name,
                        base_currency=bundle.plan.base_currency,
                        initial_balance=bundle.plan.initial_balance,
                    )
                )
                for export_entry in bundle.entries:
                    self._entry_repo.create(
                        EntryCreateDto(
                            plan_id=plan.id,
                            entry_type=export_entry.entry_type,
                            name=export_entry.name,
                            date_pattern=export_entry.date_pattern,
                            amount=export_entry.amount,
                            currency=export_entry.currency,
                            category=export_entry.category,
                            is_active=export_entry.is_active,
                        )
                    )
                self._apply_rate_changes(
                    plan_base_currency=bundle.plan.base_currency,
                    additions=additions,
                    conflicts=conflicts,
                    rate_resolutions=rate_resolutions,
                )
        except PlanImportError:
            raise
        except Exception as exc:
            raise PlanImportError(str(exc)) from exc

        return plan.id

    def _load_bundle(self, path: Path) -> PlanExportBundle:
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            msg = f"Invalid JSON in plan import file: {exc.msg}"
            raise PlanImportError(msg) from exc

        try:
            bundle = PlanExportBundle.model_validate(raw)
        except ValidationError as exc:
            msg = f"Invalid plan bundle: {exc}"
            raise PlanImportError(msg) from exc

        self._validate_format_version(bundle.format_version)
        self._validate_app_identifier(bundle.app)
        return bundle

    @staticmethod
    def _validate_app_identifier(app: str) -> None:
        if app not in SUPPORTED_IMPORT_APP_IDS:
            msg = f"Unsupported app identifier: {app}"
            raise PlanImportError(msg)

    @staticmethod
    def _validate_format_version(format_version: int) -> None:
        if format_version != _SUPPORTED_FORMAT_VERSION:
            msg = f"Unsupported format version: {format_version}"
            raise PlanImportError(msg)

    def _classify_rates(
        self,
        bundle: PlanExportBundle,
    ) -> tuple[list[PlanExportRate], list[RateConflict], list[PlanExportRate]]:
        local_rates = {
            (rate.from_currency, rate.to_currency): rate.rate
            for rate in self._exchange_rate_repo.get_all()
        }
        additions: list[PlanExportRate] = []
        conflicts: list[RateConflict] = []
        unchanged: list[PlanExportRate] = []

        for file_rate in bundle.exchange_rates:
            self._classify_single_rate(file_rate, local_rates, additions, conflicts, unchanged)

        return additions, conflicts, unchanged

    @staticmethod
    def _classify_single_rate(
        file_rate: PlanExportRate,
        local_rates: dict[tuple[str, str], float],
        additions: list[PlanExportRate],
        conflicts: list[RateConflict],
        unchanged: list[PlanExportRate],
    ) -> None:
        key = (file_rate.from_currency, file_rate.to_currency)
        local_rate = local_rates.get(key)
        if local_rate is None:
            additions.append(file_rate)
        elif abs(local_rate - file_rate.rate) > _RATE_EPSILON:
            conflicts.append(
                RateConflict(
                    from_currency=file_rate.from_currency,
                    local_rate=local_rate,
                    file_rate=file_rate.rate,
                )
            )
        else:
            unchanged.append(file_rate)

    @staticmethod
    def _validate_rate_resolutions(
        conflicts: list[RateConflict],
        rate_resolutions: dict[str, str],
    ) -> None:
        for conflict in conflicts:
            resolution = rate_resolutions.get(conflict.from_currency)
            if resolution is None:
                msg = f"Missing rate resolution for {conflict.from_currency}"
                raise PlanImportError(msg)
            if resolution not in {"keep", "use_file"}:
                msg = f"Invalid rate resolution for {conflict.from_currency}: {resolution}"
                raise PlanImportError(msg)

    @staticmethod
    def _validate_entry_patterns(bundle: PlanExportBundle) -> None:
        for entry in bundle.entries:
            try:
                parse_pattern(entry.date_pattern)
            except DatePatternParseError as exc:
                msg = f"Invalid date pattern in entry {entry.name!r}: {exc}"
                raise PlanImportError(msg) from exc

    def _resolve_import_name(self, desired_name: str) -> str:
        existing_names = {plan.name for plan in self._plan_repo.find_all()}
        if desired_name not in existing_names:
            return desired_name

        candidate = f"{desired_name}{_IMPORTED_SUFFIX}"
        while candidate in existing_names:
            candidate = f"{candidate}{_IMPORTED_SUFFIX}"
        return candidate

    def _apply_rate_changes(
        self,
        *,
        plan_base_currency: str,
        additions: list[PlanExportRate],
        conflicts: list[RateConflict],
        rate_resolutions: dict[str, str],
    ) -> None:
        updated_at = SqliteExchangeRateRepository.utc_now_iso()
        for file_rate in additions:
            self._exchange_rate_repo.upsert(
                ExchangeRateUpsertDto(
                    from_currency=file_rate.from_currency,
                    to_currency=file_rate.to_currency,
                    rate=file_rate.rate,
                    updated_at=updated_at,
                )
            )

        conflicts_by_currency = {conflict.from_currency: conflict for conflict in conflicts}
        for from_currency, resolution in rate_resolutions.items():
            if resolution != "use_file":
                continue
            conflict = conflicts_by_currency.get(from_currency)
            if conflict is None:
                continue
            self._exchange_rate_repo.upsert(
                ExchangeRateUpsertDto(
                    from_currency=from_currency,
                    to_currency=plan_base_currency,
                    rate=conflict.file_rate,
                    updated_at=updated_at,
                )
            )
