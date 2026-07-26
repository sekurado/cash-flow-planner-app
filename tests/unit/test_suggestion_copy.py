from __future__ import annotations

from datetime import date

import pytest
from PySide6.QtCore import QSettings, QTranslator
from PySide6.QtWidgets import QApplication

from src.app.i18n.suggestion_copy import localize_suggestion
from src.domain.entities import Entry, EntryType, SimulationParams
from src.domain.suggestion_deficit import DEFICIT_ANALYZER_FUNCS
from src.domain.suggestion_messages import suggestion_uniform_cut_title
from src.domain.suggestion_simulation import simulate_entries
from src.domain.suggestions import Suggestion, SuggestionEngine, SuggestionKind


def _entry(
    *,
    entry_id: str,
    entry_type: EntryType,
    name: str,
    amount: float,
    date_pattern: str,
) -> Entry:
    return Entry(
        id=entry_id,
        plan_id="plan-1",
        entry_type=entry_type,
        name=name,
        date_pattern=date_pattern,
        amount=amount,
        currency="USD",
        category="general",
        is_active=True,
        created_at="2026-01-01T00:00:00Z",
    )


@pytest.mark.unit
def test_suggestion_uniform_cut_title_english(qt_app: QApplication) -> None:
    QSettings().setValue("language", "en")
    message = suggestion_uniform_cut_title(12.5)
    localized = localize_suggestion(
        Suggestion(
            id="test",
            kind=SuggestionKind.AVOID_DEFICIT,
            priority=1,
            title=message.text,
            detail="",
            impact_amount=None,
            impact_currency="USD",
            title_template=message.template,
            title_args=message.args,
        )
    )
    assert localized.title == "Cut recurring expenses by 12.5%"


@pytest.mark.unit
def test_suggestion_uniform_cut_title_french(qt_app: QApplication) -> None:
    import src.app.resources_rc  # noqa: F401

    translator = QTranslator()
    assert translator.load(":/i18n/app_fr.qm")
    qt_app.installTranslator(translator)
    QSettings().setValue("language", "fr")

    try:
        message = suggestion_uniform_cut_title(10.0)
        localized = localize_suggestion(
            Suggestion(
                id="test",
                kind=SuggestionKind.AVOID_DEFICIT,
                priority=1,
                title=message.text,
                detail="",
                impact_amount=None,
                impact_currency="USD",
                title_template=message.template,
                title_args=message.args,
            )
        )
        assert localized.title == "Réduire les dépenses récurrentes de 10%"
    finally:
        QSettings().setValue("language", "en")
        qt_app.removeTranslator(translator)


@pytest.mark.unit
def test_deficit_engine_suggestions_include_translation_templates() -> None:
    params = SimulationParams(
        start_date=date(2026, 1, 1),
        end_date=date(2026, 3, 31),
        initial_balance=200.0,
        base_currency="USD",
    )
    entries = [
        _entry(
            entry_id="income-1",
            entry_type=EntryType.INCOME,
            name="Salary",
            amount=500.0,
            date_pattern="1..",
        ),
        _entry(
            entry_id="expense-1",
            entry_type=EntryType.EXPENSE,
            name="Rent",
            amount=900.0,
            date_pattern="5..",
        ),
    ]
    result = simulate_entries(entries, params, plan_id="plan-1")
    engine = SuggestionEngine(analyzers=list(DEFICIT_ANALYZER_FUNCS))
    suggestions = engine.analyze(entries, result)

    assert suggestions
    assert any(suggestion.title_template for suggestion in suggestions)
