from __future__ import annotations

import pytest
from sqlalchemy.engine import Connection

from src.app.viewmodels.currency_vm import CurrencyViewModel
from src.data.repositories.exchange_rate_repo import (
    ExchangeRateUpsertDto,
    SqliteExchangeRateRepository,
)
from src.data.repositories.plan_repo import PlanCreateDto, SqlitePlanRepository


@pytest.fixture
def currency_view_model(
    exchange_rate_repository: SqliteExchangeRateRepository,
) -> CurrencyViewModel:
    return CurrencyViewModel(exchange_rate_repository)


def test_load_rates_filters_by_base_currency(
    db_conn: Connection,
    currency_view_model: CurrencyViewModel,
) -> None:
    rate_repo = SqliteExchangeRateRepository(db_conn)
    rate_repo.upsert(
        ExchangeRateUpsertDto(
            from_currency="EUR",
            to_currency="USD",
            rate=1.1,
            updated_at="2026-01-01T00:00:00+00:00",
        )
    )
    rate_repo.upsert(
        ExchangeRateUpsertDto(
            from_currency="EUR",
            to_currency="GBP",
            rate=0.85,
            updated_at="2026-01-01T00:00:00+00:00",
        )
    )

    currency_view_model.loadRates("USD")

    assert len(currency_view_model.rates) == 1
    assert currency_view_model.rates[0]["from_currency"] == "EUR"
    assert currency_view_model.rates[0]["to_currency"] == "USD"


def test_create_rate_appends_to_list(
    currency_view_model: CurrencyViewModel,
) -> None:
    currency_view_model.loadRates("USD")

    currency_view_model.createRate("GBP", "USD", 1.25)

    assert len(currency_view_model.rates) == 1
    assert currency_view_model.rates[0]["rate"] == 1.25


def test_create_rate_allows_non_usd_target(
    currency_view_model: CurrencyViewModel,
) -> None:
    currency_view_model.loadRates("GBP")

    currency_view_model.createRate("EUR", "GBP", 0.85)

    assert currency_view_model.error == ""
    assert len(currency_view_model.rates) == 1
    assert currency_view_model.rates[0]["from_currency"] == "EUR"
    assert currency_view_model.rates[0]["to_currency"] == "GBP"


def test_update_rate_changes_value(
    db_conn: Connection,
    currency_view_model: CurrencyViewModel,
) -> None:
    rate_repo = SqliteExchangeRateRepository(db_conn)
    rate_repo.upsert(
        ExchangeRateUpsertDto(
            from_currency="EUR",
            to_currency="USD",
            rate=1.1,
            updated_at="2026-01-01T00:00:00+00:00",
        )
    )
    currency_view_model.loadRates("USD")

    currency_view_model.updateRate("EUR", "USD", 1.2)

    assert currency_view_model.rates[0]["rate"] == 1.2


def test_delete_rate_removes_from_list(
    db_conn: Connection,
    currency_view_model: CurrencyViewModel,
) -> None:
    rate_repo = SqliteExchangeRateRepository(db_conn)
    rate_repo.upsert(
        ExchangeRateUpsertDto(
            from_currency="EUR",
            to_currency="USD",
            rate=1.1,
            updated_at="2026-01-01T00:00:00+00:00",
        )
    )
    currency_view_model.loadRates("USD")

    currency_view_model.deleteRate("EUR", "USD")

    assert currency_view_model.rates == []


def test_create_rate_rejects_same_source_and_target(
    currency_view_model: CurrencyViewModel,
) -> None:
    currency_view_model.loadRates("GBP")

    currency_view_model.createRate("EUR", "EUR", 1.0)

    assert currency_view_model.error != ""
    assert currency_view_model.rates == []


def test_delete_all_rates_clears_db_and_list(
    db_conn: Connection,
    currency_view_model: CurrencyViewModel,
) -> None:
    rate_repo = SqliteExchangeRateRepository(db_conn)
    rate_repo.upsert(
        ExchangeRateUpsertDto(
            from_currency="EUR",
            to_currency="USD",
            rate=1.1,
            updated_at="2026-01-01T00:00:00+00:00",
        )
    )
    rate_repo.upsert(
        ExchangeRateUpsertDto(
            from_currency="GBP",
            to_currency="EUR",
            rate=1.15,
            updated_at="2026-01-01T00:00:00+00:00",
        )
    )
    currency_view_model.loadRates("USD")

    currency_view_model.deleteAllRates()

    assert currency_view_model.rates == []
    assert currency_view_model.error == ""
    assert rate_repo.get_all() == []


def test_rates_shared_across_plans(
    db_conn: Connection,
    currency_view_model: CurrencyViewModel,
) -> None:
    plan_repo = SqlitePlanRepository(db_conn)
    plan_repo.create(PlanCreateDto(name="Plan A", base_currency="USD", initial_balance=0))
    plan_repo.create(PlanCreateDto(name="Plan B", base_currency="EUR", initial_balance=0))
    currency_view_model.createRate("GBP", "USD", 1.3)
    currency_view_model.loadRates("USD")

    assert len(currency_view_model.rates) == 1
