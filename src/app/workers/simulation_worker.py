from __future__ import annotations

from dataclasses import asdict, is_dataclass
from datetime import date

from pydantic import BaseModel
from PySide6.QtCore import QObject, QRunnable, Signal

from src.data.repositories.entry_repo import AbstractEntryRepository
from src.data.repositories.exchange_rate_repo import AbstractExchangeRateRepository
from src.domain.currency_normalizer import normalize_all
from src.domain.date_pattern import expand_all
from src.domain.entities import (
    DailyBalance,
    Entry,
    MonthlySnapshot,
    SimulationParams,
    SimulationResult,
)
from src.domain.simulation_engine import SimulationEngine

JsonPrimitive = str | int | float | bool | None
JsonValue = JsonPrimitive | list["JsonValue"] | dict[str, "JsonValue"]


class SimulationWorkerSignals(QObject):
    finished = Signal(dict)
    error = Signal(str)


class SimulationWorker(QRunnable):
    def __init__(
        self,
        entry_repo: AbstractEntryRepository,
        exchange_rate_repo: AbstractExchangeRateRepository,
        plan_id: str,
        params: SimulationParams,
        what_if_overrides: dict[str, dict[str, object]] | None = None,
    ) -> None:
        super().__init__()
        self._entry_repo = entry_repo
        self._exchange_rate_repo = exchange_rate_repo
        self._plan_id = plan_id
        self._params = params
        self._what_if_overrides = what_if_overrides
        self.signals = SimulationWorkerSignals()

    def run(self) -> None:
        try:
            result = run_plan_simulation(
                self._entry_repo,
                self._exchange_rate_repo,
                self._plan_id,
                self._params,
                what_if_overrides=self._what_if_overrides,
            )
            self.signals.finished.emit(serialize_simulation_result(result))
        except Exception as exc:
            self.signals.error.emit(str(exc))


def prepare_entries(
    entries: list[Entry],
    what_if_overrides: dict[str, dict[str, object]] | None,
) -> list[Entry]:
    if not what_if_overrides:
        return entries
    patched: list[Entry] = []
    for entry in entries:
        override = what_if_overrides.get(entry.id, {})
        if override:
            entry = entry.model_copy(update=override)
        patched.append(entry)
    return patched


def run_plan_simulation(
    entry_repo: AbstractEntryRepository,
    exchange_rate_repo: AbstractExchangeRateRepository,
    plan_id: str,
    params: SimulationParams,
    what_if_overrides: dict[str, dict[str, object]] | None = None,
) -> SimulationResult:
    entries = entry_repo.find_by_plan_id(plan_id)
    entries = prepare_entries(entries, what_if_overrides)
    events = expand_all(entries, params.start_date, params.end_date)
    rates = exchange_rate_repo.get_all()
    normalized = normalize_all(events, params.base_currency, rates)
    return SimulationEngine.run(normalized, params, plan_id=plan_id)


def serialize_simulation_result(result: SimulationResult) -> dict[str, JsonValue]:
    serialized = _serialize_value(asdict(result))
    assert isinstance(serialized, dict)
    return serialized


def deserialize_simulation_result(data: dict[str, JsonValue]) -> SimulationResult:
    params_raw = data.get("params")
    if not isinstance(params_raw, dict):
        msg = "Simulation result is missing params"
        raise TypeError(msg)

    start_date = params_raw.get("start_date")
    end_date = params_raw.get("end_date")
    initial_balance = params_raw.get("initial_balance")
    base_currency = params_raw.get("base_currency")
    if not isinstance(start_date, str) or not isinstance(end_date, str):
        msg = "Simulation params must include ISO start_date and end_date"
        raise TypeError(msg)
    if not isinstance(initial_balance, (int, float)):
        msg = "Simulation params must include a numeric initial_balance"
        raise TypeError(msg)
    if not isinstance(base_currency, str) or not base_currency:
        msg = "Simulation params must include a non-empty base_currency"
        raise TypeError(msg)

    daily_balances_raw = data.get("daily_balances")
    daily_balances: tuple[DailyBalance, ...] = ()
    if isinstance(daily_balances_raw, list):
        days: list[DailyBalance] = []
        for item in daily_balances_raw:
            daily = _parse_daily_balance(item)
            if daily is not None:
                days.append(daily)
        daily_balances = tuple(days)

    monthly_snapshots_raw = data.get("monthly_snapshots")
    monthly_snapshots: tuple[MonthlySnapshot, ...] = ()
    if isinstance(monthly_snapshots_raw, list):
        snapshots: list[MonthlySnapshot] = []
        for item in monthly_snapshots_raw:
            snapshot = _parse_monthly_snapshot(item)
            if snapshot is not None:
                snapshots.append(snapshot)
        monthly_snapshots = tuple(snapshots)

    first_deficit_raw = data.get("first_deficit_date")
    first_deficit_date = (
        date.fromisoformat(first_deficit_raw) if isinstance(first_deficit_raw, str) else None
    )

    plan_id = data.get("plan_id")
    final_balance = data.get("final_balance")
    total_income = data.get("total_income")
    total_expense = data.get("total_expense")
    if not isinstance(plan_id, str):
        msg = "Simulation result is missing plan_id"
        raise TypeError(msg)
    if not isinstance(final_balance, (int, float)):
        msg = "Simulation result is missing final_balance"
        raise TypeError(msg)
    if not isinstance(total_income, (int, float)):
        msg = "Simulation result is missing total_income"
        raise TypeError(msg)
    if not isinstance(total_expense, (int, float)):
        msg = "Simulation result is missing total_expense"
        raise TypeError(msg)

    return SimulationResult(
        plan_id=plan_id,
        params=SimulationParams(
            start_date=date.fromisoformat(start_date),
            end_date=date.fromisoformat(end_date),
            initial_balance=float(initial_balance),
            base_currency=base_currency,
        ),
        daily_balances=daily_balances,
        monthly_snapshots=monthly_snapshots,
        first_deficit_date=first_deficit_date,
        first_deficit_event=None,
        final_balance=float(final_balance),
        total_income=float(total_income),
        total_expense=float(total_expense),
    )


def _parse_daily_balance(item: object) -> DailyBalance | None:
    if not isinstance(item, dict):
        return None
    date_raw = item.get("date")
    day_income = item.get("day_income")
    day_expense = item.get("day_expense")
    closing_balance = item.get("closing_balance")
    if not isinstance(date_raw, str):
        return None
    if not isinstance(day_income, (int, float)):
        return None
    if not isinstance(day_expense, (int, float)):
        return None
    if not isinstance(closing_balance, (int, float)):
        return None
    try:
        parsed_date = date.fromisoformat(date_raw)
    except ValueError:
        return None
    return DailyBalance(
        date=parsed_date,
        events=(),
        day_income=float(day_income),
        day_expense=float(day_expense),
        closing_balance=float(closing_balance),
    )


def _parse_monthly_snapshot(item: object) -> MonthlySnapshot | None:
    if not isinstance(item, dict):
        return None
    year = item.get("year")
    month = item.get("month")
    total_income = item.get("total_income")
    total_expense = item.get("total_expense")
    net_flow = item.get("net_flow")
    closing_balance = item.get("closing_balance")
    deficit = item.get("deficit")
    if not isinstance(year, (int, float)):
        return None
    if not isinstance(month, (int, float)):
        return None
    if not isinstance(total_income, (int, float)):
        return None
    if not isinstance(total_expense, (int, float)):
        return None
    if not isinstance(net_flow, (int, float)):
        return None
    if not isinstance(closing_balance, (int, float)):
        return None
    if not isinstance(deficit, (bool, int)):
        return None
    return MonthlySnapshot(
        year=int(year),
        month=int(month),
        total_income=float(total_income),
        total_expense=float(total_expense),
        net_flow=float(net_flow),
        closing_balance=float(closing_balance),
        deficit=bool(deficit),
    )


def _serialize_value(value: object) -> JsonValue:
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, BaseModel):
        return value.model_dump(mode="json")
    if is_dataclass(value):
        return {
            field: _serialize_value(getattr(value, field)) for field in value.__dataclass_fields__
        }
    if isinstance(value, dict):
        return {key: _serialize_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_serialize_value(item) for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    msg = f"Unsupported value type for simulation serialization: {type(value)!r}"
    raise TypeError(msg)
