from __future__ import annotations

import pytest
from PySide6.QtCore import QSettings, QTranslator
from PySide6.QtWidgets import QApplication

from src.app.i18n.user_messages import (
    describe_pattern_text,
    translate_user_message,
    validation_error_message,
)


@pytest.fixture
def qt_app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app  # type: ignore[return-value]


@pytest.mark.unit
def test_describe_pattern_monthly_english(qt_app: QApplication) -> None:
    QSettings().setValue("language", "en")
    assert describe_pattern_text("10..") == "Monthly on the 10th"


@pytest.mark.unit
def test_describe_pattern_invalid_returns_empty(qt_app: QApplication) -> None:
    assert describe_pattern_text("not-valid") == ""


@pytest.mark.unit
def test_describe_pattern_monthly_russian(qt_app: QApplication) -> None:
    import src.app.resources_rc  # noqa: F401

    translator = QTranslator()
    assert translator.load(":/i18n/app_ru.qm")
    qt_app.installTranslator(translator)
    QSettings().setValue("language", "ru")

    try:
        assert describe_pattern_text("10..") == "Ежемесячно 10"
        assert describe_pattern_text("15.03.") == "Ежегодно 15 мар."
    finally:
        QSettings().setValue("language", "en")
        qt_app.removeTranslator(translator)


@pytest.mark.unit
def test_translate_plan_not_found(qt_app: QApplication) -> None:
    translated = translate_user_message("Plan not found: abc-123")
    assert translated == "Forecast not found: abc-123"


@pytest.mark.unit
def test_translate_entry_not_found(qt_app: QApplication) -> None:
    translated = translate_user_message("Entry not found: entry-42")
    assert translated == "Cash flow not found: entry-42"


@pytest.mark.unit
def test_translate_no_projection_result(qt_app: QApplication) -> None:
    translated = translate_user_message("No simulation result to export.")
    assert translated == "No projection result to export."


@pytest.mark.unit
def test_validation_error_message_uses_translation(qt_app: QApplication) -> None:
    import src.app.resources_rc  # noqa: F401

    translator = QTranslator()
    assert translator.load(":/i18n/app_ru.qm")
    qt_app.installTranslator(translator)

    assert validation_error_message() == "Неверные данные. Проверьте введённые значения."
