from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence
from datetime import date

from pydantic import BaseModel, ConfigDict

from src.domain.currency_normalizer import convert_amount
from src.domain.entities import ExchangeRate

DEFAULT_UNCATEGORIZED_LABEL = "(Uncategorized)"
DEFAULT_NO_PLACE_LABEL = "(No place)"
DEFAULT_OTHER_LABEL = "Other"


class ExpenseAnalyticsExpense(BaseModel):
    """Expense row enriched with dictionary labels for analytics rollups."""

    model_config = ConfigDict(frozen=True)

    amount: float
    currency: str
    occurred_on: date
    name_id: str
    name_label: str
    category_id: str | None = None
    category_label: str | None = None
    place_id: str | None = None
    place_label: str | None = None


class ExpenseAnalyticsBucket(BaseModel):
    model_config = ConfigDict(frozen=True)

    label: str
    id: str | None = None
    total_amount: float
    transaction_count: int
    percent_of_total: float


class ExpenseAnalyticsRollups(BaseModel):
    model_config = ConfigDict(frozen=True)

    total_amount: float
    display_currency: str
    by_name: tuple[ExpenseAnalyticsBucket, ...]
    by_category: tuple[ExpenseAnalyticsBucket, ...]
    by_place: tuple[ExpenseAnalyticsBucket, ...]


class ExpenseAnalyticsEngine:
    @staticmethod
    def aggregate(
        expenses: Sequence[ExpenseAnalyticsExpense],
        *,
        start_date: date,
        end_date: date,
        display_currency: str,
        exchange_rates: list[ExchangeRate],
        uncategorized_label: str = DEFAULT_UNCATEGORIZED_LABEL,
        no_place_label: str = DEFAULT_NO_PLACE_LABEL,
    ) -> ExpenseAnalyticsRollups:
        """Aggregate expenses in an inclusive date range into name/category/place buckets."""
        if start_date > end_date:
            msg = "start_date must be on or before end_date"
            raise ValueError(msg)

        normalized_currency = display_currency.strip().upper()
        in_range = [
            expense for expense in expenses if start_date <= expense.occurred_on <= end_date
        ]

        name_items: list[tuple[float, str | None, str]] = []
        category_items: list[tuple[float, str | None, str]] = []
        place_items: list[tuple[float, str | None, str]] = []
        total_amount = 0.0

        for expense in in_range:
            normalized_amount = convert_amount(
                expense.amount,
                expense.currency,
                normalized_currency,
                exchange_rates,
            )
            total_amount += normalized_amount
            name_items.append((normalized_amount, expense.name_id, expense.name_label))
            category_items.append(
                (
                    normalized_amount,
                    expense.category_id,
                    expense.category_label
                    if expense.category_label is not None
                    else uncategorized_label,
                )
            )
            place_items.append(
                (
                    normalized_amount,
                    expense.place_id,
                    expense.place_label if expense.place_label is not None else no_place_label,
                )
            )

        return ExpenseAnalyticsRollups(
            total_amount=total_amount,
            display_currency=normalized_currency,
            by_name=_build_buckets(name_items, total_amount),
            by_category=_build_buckets(category_items, total_amount),
            by_place=_build_buckets(place_items, total_amount),
        )


def group_top_n(
    buckets: Sequence[ExpenseAnalyticsBucket],
    top_n: int,
    *,
    other_label: str = DEFAULT_OTHER_LABEL,
) -> tuple[ExpenseAnalyticsBucket, ...]:
    """Keep the largest *top_n* buckets and merge the remainder into *other_label*."""
    if top_n <= 0:
        return ()

    ordered = sorted(buckets, key=lambda bucket: (-bucket.total_amount, bucket.label.lower()))
    if len(ordered) <= top_n:
        return tuple(ordered)

    top = ordered[:top_n]
    remainder = ordered[top_n:]
    other_total = sum(bucket.total_amount for bucket in remainder)
    other_count = sum(bucket.transaction_count for bucket in remainder)
    grand_total = sum(bucket.total_amount for bucket in ordered)
    other_percent = (other_total / grand_total * 100.0) if grand_total else 0.0
    other_bucket = ExpenseAnalyticsBucket(
        label=other_label,
        id=None,
        total_amount=other_total,
        transaction_count=other_count,
        percent_of_total=other_percent,
    )
    return (*top, other_bucket)


def _build_buckets(
    items: Sequence[tuple[float, str | None, str]],
    grand_total: float,
) -> tuple[ExpenseAnalyticsBucket, ...]:
    totals: dict[tuple[str | None, str], list[float]] = defaultdict(list)
    for amount, dimension_id, label in items:
        totals[(dimension_id, label)].append(amount)

    buckets: list[ExpenseAnalyticsBucket] = []
    for (dimension_id, label), amounts in totals.items():
        bucket_total = sum(amounts)
        buckets.append(
            ExpenseAnalyticsBucket(
                label=label,
                id=dimension_id,
                total_amount=bucket_total,
                transaction_count=len(amounts),
                percent_of_total=(bucket_total / grand_total * 100.0) if grand_total else 0.0,
            )
        )

    buckets.sort(key=lambda bucket: (-bucket.total_amount, bucket.label.lower()))
    return tuple(buckets)
