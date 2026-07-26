from __future__ import annotations

import pytest
from PySide6.QtCore import QCoreApplication, QTranslator

import src.app.resources_rc  # noqa: F401

_SCENARIO_DISCLAIMER_SOURCE = (
    "Based on the saved forecast — the chart above reflects your scenario."
)
_SCENARIO_DISCLAIMER_TRANSLATIONS = {
    "en": _SCENARIO_DISCLAIMER_SOURCE,
    "fr": "Basé sur la prévision enregistrée — le graphique ci-dessus reflète votre scénario.",
    "de": "Basierend auf der gespeicherten Prognose — die Grafik oben zeigt Ihr Szenario.",
    "ru": "На основе сохранённого прогноза — график выше отражает ваш сценарий.",
    "es": "Según el pronóstico guardado — el gráfico anterior refleja su escenario.",
}


@pytest.mark.unit
@pytest.mark.parametrize("locale", tuple(_SCENARIO_DISCLAIMER_TRANSLATIONS))
def test_scenario_disclaimer_translates_in_embedded_catalog(
    qt_app: QCoreApplication,
    locale: str,
) -> None:
    translator = QTranslator()
    assert translator.load(f":/i18n/app_{locale}.qm")

    translated = translator.translate("SuggestionsPanel", _SCENARIO_DISCLAIMER_SOURCE)
    assert translated == _SCENARIO_DISCLAIMER_TRANSLATIONS[locale]
