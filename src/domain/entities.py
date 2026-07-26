from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import StrEnum

from pydantic import BaseModel, ConfigDict


class EntryType(StrEnum):
    INCOME = "income"
    EXPENSE = "expense"


class Plan(BaseModel):
    id: str
    name: str
    base_currency: str
    initial_balance: float
    created_at: str
    updated_at: str


class Entry(BaseModel):
    id: str
    plan_id: str
    entry_type: EntryType
    name: str
    date_pattern: str
    amount: float
    currency: str
    category: str | None = None
    is_active: bool = True
    created_at: str


class EntryCreateDTO(BaseModel):
    """Row parsed from an import file, ready to be persisted with a plan_id."""

    entry_type: EntryType
    name: str
    date_pattern: str
    amount: float
    currency: str
    category: str | None = None
    is_active: bool = True


class ImportRowError(BaseModel):
    model_config = ConfigDict(frozen=True)

    row_number: int
    error_message: str


class ImportResult(BaseModel):
    valid_rows: list[EntryCreateDTO]
    errors: list[ImportRowError]


class PlanExportEntry(BaseModel):
    model_config = ConfigDict(frozen=True)

    entry_type: EntryType
    name: str
    date_pattern: str
    amount: float
    currency: str
    category: str | None = None
    is_active: bool = True


class PlanExportRate(BaseModel):
    model_config = ConfigDict(frozen=True)

    from_currency: str
    to_currency: str
    rate: float


class PlanExportPlan(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str
    base_currency: str
    initial_balance: float


class PlanExportBundle(BaseModel):
    model_config = ConfigDict(frozen=True)

    format_version: int
    app: str
    exported_at: str
    plan: PlanExportPlan
    entries: list[PlanExportEntry]
    exchange_rates: list[PlanExportRate]
    metadata: dict[str, str] | None = None


class RateConflict(BaseModel):
    model_config = ConfigDict(frozen=True)

    from_currency: str
    local_rate: float
    file_rate: float


class PlanImportPreview(BaseModel):
    model_config = ConfigDict(frozen=True)

    bundle: PlanExportBundle
    rate_additions: list[PlanExportRate]
    rate_conflicts: list[RateConflict]
    rate_unchanged: list[PlanExportRate] = []


class ExchangeRate(BaseModel):
    from_currency: str
    to_currency: str
    rate: float
    updated_at: str


class SimulationRun(BaseModel):
    id: str
    plan_id: str
    start_date: date
    end_date: date
    result_json: str
    created_at: str


class AuditLogEntry(BaseModel):
    id: str
    plan_id: str
    entity_type: str
    entity_id: str
    action: str
    summary: str
    timestamp: str


class FinancialEvent(BaseModel):
    model_config = ConfigDict(frozen=True)

    entry_id: str
    entry_name: str
    date: date
    type: EntryType
    amount: float
    currency: str
    category: str | None = None


class NormalizedEvent(BaseModel):
    model_config = ConfigDict(frozen=True)

    entry_id: str
    entry_name: str
    date: date
    type: EntryType
    normalized_amount: float
    base_currency: str
    category: str | None = None


@dataclass(frozen=True)
class SimulationParams:
    start_date: date
    end_date: date
    initial_balance: float
    base_currency: str


@dataclass(frozen=True)
class DailyBalance:
    date: date
    events: tuple[NormalizedEvent, ...]
    day_income: float
    day_expense: float
    closing_balance: float


@dataclass(frozen=True)
class MonthlySnapshot:
    year: int
    month: int
    total_income: float
    total_expense: float
    net_flow: float
    closing_balance: float
    deficit: bool


@dataclass(frozen=True)
class SimulationResult:
    plan_id: str
    params: SimulationParams
    daily_balances: tuple[DailyBalance, ...]
    monthly_snapshots: tuple[MonthlySnapshot, ...]
    first_deficit_date: date | None
    first_deficit_event: NormalizedEvent | None
    final_balance: float
    total_income: float
    total_expense: float
