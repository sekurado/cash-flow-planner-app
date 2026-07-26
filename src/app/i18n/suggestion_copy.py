from __future__ import annotations

from dataclasses import replace

from PySide6.QtCore import QCoreApplication

from src.domain.suggestions import Suggestion

_SUGGESTION_CONTEXT = "CashFlowSuggestions"


def localize_suggestion(suggestion: Suggestion) -> Suggestion:
    return replace(
        suggestion,
        title=_localize(suggestion.title_template, suggestion.title_args, suggestion.title),
        detail=_localize(suggestion.detail_template, suggestion.detail_args, suggestion.detail),
    )


def localize_suggestions(suggestions: list[Suggestion]) -> list[Suggestion]:
    return [localize_suggestion(suggestion) for suggestion in suggestions]


def _localize(template: str, args: tuple[str, ...], fallback: str) -> str:
    source = template or fallback
    translated = QCoreApplication.translate(_SUGGESTION_CONTEXT, source)
    if not args:
        return translated
    result = translated
    for index, arg in enumerate(args, start=1):
        result = result.replace(f"%{index}", arg)
    return result


def _register_i18n_catalog() -> None:
    """Literal translate() calls for pyside6-lupdate extraction only."""
    QCoreApplication.translate("CashFlowSuggestions", "Cut recurring expenses by %1%")
    QCoreApplication.translate(
        "CashFlowSuggestions",
        "A uniform %1% reduction across recurring expenses saves about %2 per month and "
        "removes the projected cash shortfall.",
    )
    QCoreApplication.translate("CashFlowSuggestions", "Reduce %1")
    QCoreApplication.translate(
        "CashFlowSuggestions",
        "Lowering %1 by %2 per occurrence is enough to avoid the projected cash shortfall "
        "if no other cash flows change.",
    )
    QCoreApplication.translate("CashFlowSuggestions", "Add %1 recurring income per month")
    QCoreApplication.translate(
        "CashFlowSuggestions",
        "Increasing recurring income by about %1 per month keeps the projection non-negative "
        "through the horizon.",
    )
    QCoreApplication.translate("CashFlowSuggestions", "Increase opening balance by %1")
    QCoreApplication.translate(
        "CashFlowSuggestions",
        "Raising the opening balance by %1 provides enough cushion to stay positive through "
        "the projection period.",
    )
    QCoreApplication.translate("CashFlowSuggestions", "Consider deferring %1")
    QCoreApplication.translate(
        "CashFlowSuggestions",
        "%1 is scheduled on %2, within 30 days of the projected cash shortfall on %3. "
        "Deferring this one-time expense may extend runway.",
    )
    QCoreApplication.translate("CashFlowSuggestions", "Review %1 spending")
    QCoreApplication.translate(
        "CashFlowSuggestions",
        "%1 averages %2 per month in this projection. Trimming discretionary categories is an "
        "easy way to save more.",
    )
    QCoreApplication.translate("CashFlowSuggestions", "You could save %1 more per month")
    QCoreApplication.translate(
        "CashFlowSuggestions",
        "The projection stays positive if recurring expenses rise by up to %1 per month — the "
        "same amount you could redirect to savings.",
    )
    QCoreApplication.translate("CashFlowSuggestions", "Build a %1 cash buffer")
    QCoreApplication.translate(
        "CashFlowSuggestions",
        "Your ending balance of %1 is thin relative to monthly outflows. Aim for at least %2 "
        "to absorb normal variability.",
    )
    QCoreApplication.translate("CashFlowSuggestions", "About %1 months of runway")
    QCoreApplication.translate(
        "CashFlowSuggestions",
        "At the current burn rate, %1 covers roughly %2 months of net cash outflow through "
        "the projection period.",
    )
