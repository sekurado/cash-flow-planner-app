from __future__ import annotations

import pytest
from PySide6.QtCore import QSettings, QTranslator
from PySide6.QtWidgets import QApplication

from src.app.i18n.pdf_messages import (
    pdf_cash_bridge_headers,
    pdf_report_title,
    pdf_section_monthly_cash_bridge,
)


@pytest.fixture
def qt_app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app  # type: ignore[return-value]


@pytest.mark.unit
def test_pdf_report_title_english(qt_app: QApplication) -> None:
    QSettings().setValue("language", "en")
    assert pdf_report_title("My Forecast") == "My Forecast — Projection report"


@pytest.mark.unit
def test_pdf_section_monthly_cash_bridge_english(qt_app: QApplication) -> None:
    QSettings().setValue("language", "en")
    assert pdf_section_monthly_cash_bridge() == "Monthly cash bridge"


@pytest.mark.unit
def test_pdf_cash_bridge_headers_english(qt_app: QApplication) -> None:
    QSettings().setValue("language", "en")
    assert pdf_cash_bridge_headers() == (
        "Year",
        "Month",
        "Opening",
        "Inflows",
        "Outflows",
        "Net",
        "Closing",
    )


@pytest.mark.unit
def test_pdf_messages_french_translations(qt_app: QApplication) -> None:
    import src.app.resources_rc  # noqa: F401

    translator = QTranslator()
    assert translator.load(":/i18n/app_fr.qm")
    qt_app.installTranslator(translator)
    QSettings().setValue("language", "fr")

    try:
        assert pdf_section_monthly_cash_bridge() == "Pont de trésorerie mensuel"
        assert pdf_cash_bridge_headers()[0] == "Année"
    finally:
        QSettings().setValue("language", "en")
        qt_app.removeTranslator(translator)


@pytest.mark.unit
def test_pdf_messages_russian_translations(qt_app: QApplication) -> None:
    import src.app.resources_rc  # noqa: F401

    translator = QTranslator()
    assert translator.load(":/i18n/app_ru.qm")
    qt_app.installTranslator(translator)
    QSettings().setValue("language", "ru")

    try:
        assert pdf_section_monthly_cash_bridge() == "Ежемесячный денежный мост"
        assert pdf_cash_bridge_headers()[0] == "Год"
    finally:
        QSettings().setValue("language", "en")
        qt_app.removeTranslator(translator)
