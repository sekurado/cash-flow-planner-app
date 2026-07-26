"""English source strings for cash-flow suggestions.

Templates use Qt ``%1``, ``%2`` placeholders for ``pyside6-lupdate`` extraction
(``CashFlowSuggestions`` context in ``src/app/i18n/suggestion_copy.py``).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TypedDict


class SuggestionCopyFields(TypedDict):
    title: str
    title_template: str
    title_args: tuple[str, ...]
    detail: str
    detail_template: str
    detail_args: tuple[str, ...]


@dataclass(frozen=True)
class SuggestionMessage:
    text: str
    template: str
    args: tuple[str, ...] = ()


def format_currency_amount(amount: float, currency: str) -> str:
    return f"{currency} {amount:,.2f}"


def _format_percent(cut_percent: float) -> str:
    rounded = round(cut_percent, 1)
    return f"{rounded:g}"


def _format_template(template: str, args: tuple[str, ...]) -> str:
    text = template
    for index, arg in enumerate(args, start=1):
        text = text.replace(f"%{index}", arg)
    return text


def _message(template: str, *args: str) -> SuggestionMessage:
    arg_tuple = tuple(args)
    return SuggestionMessage(
        text=_format_template(template, arg_tuple),
        template=template,
        args=arg_tuple,
    )


UNIFORM_CUT_TITLE = "Cut recurring expenses by %1%"
UNIFORM_CUT_DETAIL = (
    "A uniform %1% reduction across recurring expenses saves about %2 per month and "
    "removes the projected cash shortfall."
)
TOP_EXPENSE_TITLE = "Reduce %1"
TOP_EXPENSE_DETAIL = (
    "Lowering %1 by %2 per occurrence is enough to avoid the projected cash shortfall "
    "if no other cash flows change."
)
INCOME_BOOST_TITLE = "Add %1 recurring income per month"
INCOME_BOOST_DETAIL = (
    "Increasing recurring income by about %1 per month keeps the projection non-negative "
    "through the horizon."
)
OPENING_BALANCE_TITLE = "Increase opening balance by %1"
OPENING_BALANCE_DETAIL = (
    "Raising the opening balance by %1 provides enough cushion to stay positive through "
    "the projection period."
)
DEFER_EXPENSE_TITLE = "Consider deferring %1"
DEFER_EXPENSE_DETAIL = (
    "%1 is scheduled on %2, within 30 days of the projected cash shortfall on %3. "
    "Deferring this one-time expense may extend runway."
)
LARGEST_CATEGORY_TITLE = "Review %1 spending"
LARGEST_CATEGORY_DETAIL = (
    "%1 averages %2 per month in this projection. Trimming discretionary categories is an "
    "easy way to save more."
)
SURPLUS_HEADROOM_TITLE = "You could save %1 more per month"
SURPLUS_HEADROOM_DETAIL = (
    "The projection stays positive if recurring expenses rise by up to %1 per month — the "
    "same amount you could redirect to savings."
)
LOW_ENDING_BALANCE_TITLE = "Build a %1 cash buffer"
LOW_ENDING_BALANCE_DETAIL = (
    "Your ending balance of %1 is thin relative to monthly outflows. Aim for at least %2 "
    "to absorb normal variability."
)
POSITIVE_RUNWAY_TITLE = "About %1 months of runway"
POSITIVE_RUNWAY_DETAIL = (
    "At the current burn rate, %1 covers roughly %2 months of net cash outflow through "
    "the projection period."
)


def suggestion_uniform_cut_title(cut_percent: float) -> SuggestionMessage:
    return _message(UNIFORM_CUT_TITLE, _format_percent(cut_percent))


def suggestion_uniform_cut_detail(
    cut_percent: float,
    monthly_savings: float,
    currency: str,
) -> SuggestionMessage:
    savings = format_currency_amount(monthly_savings, currency)
    return _message(UNIFORM_CUT_DETAIL, _format_percent(cut_percent), savings)


def suggestion_top_expense_title(entry_name: str) -> SuggestionMessage:
    return _message(TOP_EXPENSE_TITLE, entry_name)


def suggestion_top_expense_detail(
    entry_name: str,
    cut_amount: float,
    currency: str,
) -> SuggestionMessage:
    amount = format_currency_amount(cut_amount, currency)
    return _message(TOP_EXPENSE_DETAIL, entry_name, amount)


def suggestion_income_boost_title(monthly_boost: float, currency: str) -> SuggestionMessage:
    amount = format_currency_amount(monthly_boost, currency)
    return _message(INCOME_BOOST_TITLE, amount)


def suggestion_income_boost_detail(monthly_boost: float, currency: str) -> SuggestionMessage:
    amount = format_currency_amount(monthly_boost, currency)
    return _message(INCOME_BOOST_DETAIL, amount)


def suggestion_opening_balance_title(buffer_amount: float, currency: str) -> SuggestionMessage:
    amount = format_currency_amount(buffer_amount, currency)
    return _message(OPENING_BALANCE_TITLE, amount)


def suggestion_opening_balance_detail(buffer_amount: float, currency: str) -> SuggestionMessage:
    amount = format_currency_amount(buffer_amount, currency)
    return _message(OPENING_BALANCE_DETAIL, amount)


def suggestion_defer_expense_title(entry_name: str) -> SuggestionMessage:
    return _message(DEFER_EXPENSE_TITLE, entry_name)


def suggestion_defer_expense_detail(
    entry_name: str,
    expense_date: str,
    deficit_date: str,
) -> SuggestionMessage:
    return _message(DEFER_EXPENSE_DETAIL, entry_name, expense_date, deficit_date)


def suggestion_largest_category_title(category: str) -> SuggestionMessage:
    return _message(LARGEST_CATEGORY_TITLE, category)


def suggestion_largest_category_detail(
    category: str,
    monthly_amount: float,
    currency: str,
) -> SuggestionMessage:
    amount = format_currency_amount(monthly_amount, currency)
    return _message(LARGEST_CATEGORY_DETAIL, category.title(), amount)


def suggestion_surplus_headroom_title(monthly_savings: float, currency: str) -> SuggestionMessage:
    amount = format_currency_amount(monthly_savings, currency)
    return _message(SURPLUS_HEADROOM_TITLE, amount)


def suggestion_surplus_headroom_detail(monthly_savings: float, currency: str) -> SuggestionMessage:
    amount = format_currency_amount(monthly_savings, currency)
    return _message(SURPLUS_HEADROOM_DETAIL, amount)


def suggestion_low_ending_balance_title(target_buffer: float, currency: str) -> SuggestionMessage:
    amount = format_currency_amount(target_buffer, currency)
    return _message(LOW_ENDING_BALANCE_TITLE, amount)


def suggestion_low_ending_balance_detail(
    final_balance: float,
    target_balance: float,
    currency: str,
) -> SuggestionMessage:
    current = format_currency_amount(final_balance, currency)
    target = format_currency_amount(target_balance, currency)
    return _message(LOW_ENDING_BALANCE_DETAIL, current, target)


def suggestion_positive_runway_title(runway_months: float) -> SuggestionMessage:
    return _message(POSITIVE_RUNWAY_TITLE, _format_percent(runway_months))


def suggestion_positive_runway_detail(
    runway_months: float,
    final_balance: float,
    currency: str,
) -> SuggestionMessage:
    balance = format_currency_amount(final_balance, currency)
    return _message(
        POSITIVE_RUNWAY_DETAIL,
        balance,
        _format_percent(runway_months),
    )


def suggestion_copy_fields(
    title_msg: SuggestionMessage,
    detail_msg: SuggestionMessage,
) -> SuggestionCopyFields:
    return {
        "title": title_msg.text,
        "title_template": title_msg.template,
        "title_args": title_msg.args,
        "detail": detail_msg.text,
        "detail_template": detail_msg.template,
        "detail_args": detail_msg.args,
    }
