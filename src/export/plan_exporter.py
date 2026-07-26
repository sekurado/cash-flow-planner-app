from __future__ import annotations

import json
from pathlib import Path

from src.app.identity import PYPROJECT_NAME
from src.data.repositories.entry_repo import AbstractEntryRepository
from src.data.repositories.exchange_rate_repo import AbstractExchangeRateRepository
from src.data.repositories.plan_repo import AbstractPlanRepository
from src.domain.entities import (
    Entry,
    PlanExportBundle,
    PlanExportEntry,
    PlanExportPlan,
    PlanExportRate,
)
from src.domain.exceptions import ExportError, PlanExportError
from src.export._atomic import atomic_write
from src.export.metadata import build_export_metadata, metadata_to_dict

_FORMAT_VERSION = 1


class PlanExporter:
    def __init__(
        self,
        plan_repo: AbstractPlanRepository,
        entry_repo: AbstractEntryRepository,
        exchange_rate_repo: AbstractExchangeRateRepository,
    ) -> None:
        self._plan_repo = plan_repo
        self._entry_repo = entry_repo
        self._exchange_rate_repo = exchange_rate_repo

    def export(self, plan_id: str, path: Path, *, app_version: str = "") -> None:
        plan = self._plan_repo.find_by_id(plan_id)
        if plan is None:
            msg = f"Plan not found: {plan_id}"
            raise PlanExportError(msg)

        entries = self._entry_repo.find_by_plan_id(plan_id)
        bundle = self._build_bundle(
            plan.name,
            plan.base_currency,
            plan.initial_balance,
            entries,
            app_version=app_version,
        )

        def _write(target: Path) -> None:
            payload = json.dumps(bundle.model_dump(mode="json"), indent=2, ensure_ascii=False)
            target.write_text(f"{payload}\n", encoding="utf-8")

        try:
            atomic_write(path, _write)
        except ExportError as exc:
            raise PlanExportError(str(exc)) from exc

    def _build_bundle(
        self,
        name: str,
        base_currency: str,
        initial_balance: float,
        entries: list[Entry],
        *,
        app_version: str = "",
    ) -> PlanExportBundle:
        export_entries = [
            PlanExportEntry(
                entry_type=entry.entry_type,
                name=entry.name,
                date_pattern=entry.date_pattern,
                amount=entry.amount,
                currency=entry.currency,
                category=entry.category,
                is_active=entry.is_active,
            )
            for entry in entries
        ]

        foreign_currencies = {
            entry.currency for entry in entries if entry.currency != base_currency
        }
        rates_by_pair = {
            (rate.from_currency, rate.to_currency): rate
            for rate in self._exchange_rate_repo.get_all()
        }
        export_rates = [
            PlanExportRate(
                from_currency=currency,
                to_currency=base_currency,
                rate=rates_by_pair[(currency, base_currency)].rate,
            )
            for currency in sorted(foreign_currencies)
            if (currency, base_currency) in rates_by_pair
        ]

        rate_entities = [
            rates_by_pair[(currency, base_currency)]
            for currency in sorted(foreign_currencies)
            if (currency, base_currency) in rates_by_pair
        ]
        export_metadata = build_export_metadata(
            app_version=app_version,
            display_currency=base_currency,
            exchange_rates=rate_entities,
        )

        return PlanExportBundle(
            format_version=_FORMAT_VERSION,
            app=PYPROJECT_NAME,
            exported_at=export_metadata.exported_at,
            plan=PlanExportPlan(
                name=name,
                base_currency=base_currency,
                initial_balance=initial_balance,
            ),
            entries=export_entries,
            exchange_rates=export_rates,
            metadata=metadata_to_dict(export_metadata),
        )
