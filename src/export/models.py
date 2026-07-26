from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from src.domain.entities import ExchangeRate, SimulationResult


class EntriesSummary(BaseModel):
    model_config = ConfigDict(frozen=True)

    active_income_count: int
    active_expense_count: int
    total_line_items: int


class CashBridgeMonth(BaseModel):
    model_config = ConfigDict(frozen=True)

    year: int
    month: int
    opening_balance: float
    total_inflows: float
    total_outflows: float
    net_flow: float
    closing_balance: float


class ExportContext(BaseModel):
    model_config = ConfigDict(frozen=True)

    plan_name: str
    result: SimulationResult
    entries_summary: EntriesSummary
    exchange_rates: tuple[ExchangeRate, ...]
    display_currency: str
    app_version: str
    exported_at: str
    overrides: dict[str, dict[str, object]] | None = None
    baseline_result: SimulationResult | None = None
    override_footnotes: tuple[str, ...] = ()
