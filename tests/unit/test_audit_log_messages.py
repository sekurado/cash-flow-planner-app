from __future__ import annotations

import pytest
from PySide6.QtCore import QSettings, QTranslator
from PySide6.QtWidgets import QApplication

from src.app.i18n.audit_log_messages import translate_audit_summary


@pytest.fixture
def qt_app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app  # type: ignore[return-value]


@pytest.mark.unit
def test_translate_plan_create_english(qt_app: QApplication) -> None:
    QSettings().setValue("language", "en")
    assert translate_audit_summary("Created forecast 'Q1 Runway'") == "Created forecast 'Q1 Runway'"


@pytest.mark.unit
def test_translate_entry_create_english(qt_app: QApplication) -> None:
    QSettings().setValue("language", "en")
    assert (
        translate_audit_summary("Added cash flow 'Office rent' (expense)")
        == "Added cash flow 'Office rent' (Expense)"
    )


@pytest.mark.unit
def test_translate_compound_plan_update_english(qt_app: QApplication) -> None:
    QSettings().setValue("language", "en")
    source = "Renamed forecast to 'Q1 Runway (revised)'; Updated opening balance to 25000.0"
    assert translate_audit_summary(source) == source


@pytest.mark.unit
def test_translate_entry_update_detail_english(qt_app: QApplication) -> None:
    QSettings().setValue("language", "en")
    source = "Updated cash flow 'Office rent': amount 2000.0 → 2200.0"
    assert translate_audit_summary(source) == source


@pytest.mark.unit
def test_translate_entry_update_compound_details_russian(qt_app: QApplication) -> None:
    import src.app.resources_rc  # noqa: F401

    translator = QTranslator()
    assert translator.load(":/i18n/app_ru.qm")
    qt_app.installTranslator(translator)
    QSettings().setValue("language", "ru")

    try:
        source = (
            "Updated cash flow 'Rent': renamed to 'Office rent'; "
            "type expense → income; currency USD → EUR; "
            "schedule updated; category updated"
        )
        translated = translate_audit_summary(source)
        assert "переименован в «Office rent»" in translated
        assert "тип Расход → Доходы" in translated
        assert "валюта USD → EUR" in translated
        assert "расписание обновлено" in translated
        assert "категория обновлена" in translated
        assert "renamed to" not in translated
        assert "schedule updated" not in translated
    finally:
        QSettings().setValue("language", "en")
        qt_app.removeTranslator(translator)


@pytest.mark.unit
def test_translate_plan_create_russian(qt_app: QApplication) -> None:
    import src.app.resources_rc  # noqa: F401

    translator = QTranslator()
    assert translator.load(":/i18n/app_ru.qm")
    qt_app.installTranslator(translator)
    QSettings().setValue("language", "ru")

    try:
        translated = translate_audit_summary("Created forecast 'Q1 Runway'")
        assert translated == "Создан прогноз «Q1 Runway»"
    finally:
        QSettings().setValue("language", "en")
        qt_app.removeTranslator(translator)
