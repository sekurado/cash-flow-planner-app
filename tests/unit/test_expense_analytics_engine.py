from __future__ import annotations

from datetime import date

import pytest

from src.domain.entities import ExchangeRate
from src.domain.exceptions import CurrencyConversionError
from src.domain.expense_analytics import (
    DEFAULT_NO_PLACE_LABEL,
    DEFAULT_OTHER_LABEL,
    DEFAULT_UNCATEGORIZED_LABEL,
    ExpenseAnalyticsBucket,
    ExpenseAnalyticsEngine,
    ExpenseAnalyticsExpense,
    group_top_n,
)


def _rate(
    *,
    from_currency: str,
    to_currency: str,
    rate: float,
) -> ExchangeRate:
    return ExchangeRate(
        from_currency=from_currency,
        to_currency=to_currency,
        rate=rate,
        updated_at="2026-01-01T00:00:00+00:00",
    )


def _expense(
    *,
    amount: float,
    currency: str = "USD",
    occurred_on: date = date(2026, 3, 10),
    name_id: str = "name-1",
    name_label: str = "Coffee",
    category_id: str | None = "cat-1",
    category_label: str | None = "Food",
    place_id: str | None = "place-1",
    place_label: str | None = "Cafe",
) -> ExpenseAnalyticsExpense:
    return ExpenseAnalyticsExpense(
        amount=amount,
        currency=currency,
        occurred_on=occurred_on,
        name_id=name_id,
        name_label=name_label,
        category_id=category_id,
        category_label=category_label,
        place_id=place_id,
        place_label=place_label,
    )


@pytest.mark.unit
def test_aggregate_empty_expenses_returns_zero_totals() -> None:
    result = ExpenseAnalyticsEngine.aggregate(
        [],
        start_date=date(2026, 3, 1),
        end_date=date(2026, 3, 31),
        display_currency="USD",
        exchange_rates=[],
    )

    assert result.total_amount == pytest.approx(0.0)
    assert result.by_name == ()
    assert result.by_category == ()
    assert result.by_place == ()


@pytest.mark.unit
def test_aggregate_normalizes_multi_currency_and_groups_by_dimension() -> None:
    expenses = [
        _expense(
            amount=10.0,
            currency="USD",
            name_id="n1",
            name_label="Coffee",
            category_id="c1",
            category_label="Food",
            place_id="p1",
            place_label="Cafe",
            occurred_on=date(2026, 3, 1),
        ),
        _expense(
            amount=20.0,
            currency="EUR",
            name_id="n2",
            name_label="Taxi",
            category_id="c2",
            category_label="Transport",
            place_id="p2",
            place_label="Airport",
            occurred_on=date(2026, 3, 5),
        ),
        _expense(
            amount=5.0,
            currency="USD",
            name_id="n1",
            name_label="Coffee",
            category_id="c1",
            category_label="Food",
            place_id="p1",
            place_label="Cafe",
            occurred_on=date(2026, 3, 15),
        ),
    ]
    rates = [_rate(from_currency="EUR", to_currency="USD", rate=1.1)]

    result = ExpenseAnalyticsEngine.aggregate(
        expenses,
        start_date=date(2026, 3, 1),
        end_date=date(2026, 3, 31),
        display_currency="usd",
        exchange_rates=rates,
    )

    assert result.display_currency == "USD"
    assert result.total_amount == pytest.approx(37.0)
    assert len(result.by_name) == 2
    assert result.by_name[0].label == "Taxi"
    assert result.by_name[0].total_amount == pytest.approx(22.0)
    assert result.by_name[1].label == "Coffee"
    assert result.by_name[1].total_amount == pytest.approx(15.0)
    assert result.by_name[1].transaction_count == 2
    assert result.by_name[1].percent_of_total == pytest.approx(15.0 / 37.0 * 100.0)
    assert result.by_category[0].label == "Transport"
    assert result.by_place[0].label == "Airport"


@pytest.mark.unit
def test_aggregate_excludes_expenses_outside_date_range() -> None:
    expenses = [
        _expense(amount=10.0, occurred_on=date(2026, 2, 28)),
        _expense(amount=20.0, occurred_on=date(2026, 3, 1)),
        _expense(amount=30.0, occurred_on=date(2026, 4, 1)),
    ]

    result = ExpenseAnalyticsEngine.aggregate(
        expenses,
        start_date=date(2026, 3, 1),
        end_date=date(2026, 3, 31),
        display_currency="USD",
        exchange_rates=[],
    )

    assert result.total_amount == pytest.approx(20.0)
    assert len(result.by_name) == 1
    assert result.by_name[0].transaction_count == 1


@pytest.mark.unit
def test_aggregate_uses_uncategorized_and_no_place_labels() -> None:
    expense = _expense(
        amount=12.5,
        category_id=None,
        category_label=None,
        place_id=None,
        place_label=None,
    )

    result = ExpenseAnalyticsEngine.aggregate(
        [expense],
        start_date=date(2026, 1, 1),
        end_date=date(2026, 12, 31),
        display_currency="USD",
        exchange_rates=[],
    )

    assert result.by_category[0].label == DEFAULT_UNCATEGORIZED_LABEL
    assert result.by_category[0].id is None
    assert result.by_place[0].label == DEFAULT_NO_PLACE_LABEL
    assert result.by_place[0].id is None


@pytest.mark.unit
def test_aggregate_raises_when_exchange_rate_missing() -> None:
    expense = _expense(amount=10.0, currency="EUR")

    with pytest.raises(CurrencyConversionError, match="EUR → USD"):
        ExpenseAnalyticsEngine.aggregate(
            [expense],
            start_date=date(2026, 3, 1),
            end_date=date(2026, 3, 31),
            display_currency="USD",
            exchange_rates=[],
        )


@pytest.mark.unit
def test_aggregate_rejects_inverted_date_range() -> None:
    with pytest.raises(ValueError, match="start_date"):
        ExpenseAnalyticsEngine.aggregate(
            [],
            start_date=date(2026, 3, 31),
            end_date=date(2026, 3, 1),
            display_currency="USD",
            exchange_rates=[],
        )


@pytest.mark.unit
def test_group_top_n_merges_remainder_into_other() -> None:
    buckets = (
        ExpenseAnalyticsBucket(
            label="A",
            id="a",
            total_amount=50.0,
            transaction_count=1,
            percent_of_total=50.0,
        ),
        ExpenseAnalyticsBucket(
            label="B",
            id="b",
            total_amount=30.0,
            transaction_count=1,
            percent_of_total=30.0,
        ),
        ExpenseAnalyticsBucket(
            label="C",
            id="c",
            total_amount=15.0,
            transaction_count=1,
            percent_of_total=15.0,
        ),
        ExpenseAnalyticsBucket(
            label="D",
            id="d",
            total_amount=5.0,
            transaction_count=1,
            percent_of_total=5.0,
        ),
    )

    grouped = group_top_n(buckets, 2, other_label=DEFAULT_OTHER_LABEL)

    assert len(grouped) == 3
    assert [bucket.label for bucket in grouped] == ["A", "B", DEFAULT_OTHER_LABEL]
    assert grouped[2].total_amount == pytest.approx(20.0)
    assert grouped[2].transaction_count == 2
    assert grouped[2].percent_of_total == pytest.approx(20.0)


@pytest.mark.unit
def test_group_top_n_returns_all_when_count_within_limit() -> None:
    buckets = (
        ExpenseAnalyticsBucket(
            label="Only",
            id="o",
            total_amount=10.0,
            transaction_count=1,
            percent_of_total=100.0,
        ),
    )

    assert group_top_n(buckets, 8) == buckets


@pytest.mark.unit
def test_group_top_n_returns_empty_for_non_positive_top_n() -> None:
    bucket = ExpenseAnalyticsBucket(
        label="Only",
        id="o",
        total_amount=10.0,
        transaction_count=1,
        percent_of_total=100.0,
    )

    assert group_top_n([bucket], 0) == ()
