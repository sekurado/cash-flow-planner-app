#!/usr/bin/env python3
"""Apply CashFlowSuggestions and SuggestionsPanel translations to .ts files."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
I18N_DIR = ROOT / "i18n"

TRANSLATIONS: dict[str, dict[str, str]] = {
    "en": {
        "Cut recurring expenses by %1%": "Cut recurring expenses by %1%",
        "A uniform %1% reduction across recurring expenses saves about %2 per month and removes the projected cash shortfall.": (
            "A uniform %1% reduction across recurring expenses saves about %2 per month and "
            "removes the projected cash shortfall."
        ),
        "Reduce %1": "Reduce %1",
        "Lowering %1 by %2 per occurrence is enough to avoid the projected cash shortfall if no other cash flows change.": (
            "Lowering %1 by %2 per occurrence is enough to avoid the projected cash shortfall "
            "if no other cash flows change."
        ),
        "Add %1 recurring income per month": "Add %1 recurring income per month",
        "Increasing recurring income by about %1 per month keeps the projection non-negative through the horizon.": (
            "Increasing recurring income by about %1 per month keeps the projection non-negative "
            "through the horizon."
        ),
        "Increase opening balance by %1": "Increase opening balance by %1",
        "Raising the opening balance by %1 provides enough cushion to stay positive through the projection period.": (
            "Raising the opening balance by %1 provides enough cushion to stay positive through "
            "the projection period."
        ),
        "Consider deferring %1": "Consider deferring %1",
        "%1 is scheduled on %2, within 30 days of the projected cash shortfall on %3. Deferring this one-time expense may extend runway.": (
            "%1 is scheduled on %2, within 30 days of the projected cash shortfall on %3. "
            "Deferring this one-time expense may extend runway."
        ),
        "Review %1 spending": "Review %1 spending",
        "%1 averages %2 per month in this projection. Trimming discretionary categories is an easy way to save more.": (
            "%1 averages %2 per month in this projection. Trimming discretionary categories is an "
            "easy way to save more."
        ),
        "You could save %1 more per month": "You could save %1 more per month",
        "The projection stays positive if recurring expenses rise by up to %1 per month — the same amount you could redirect to savings.": (
            "The projection stays positive if recurring expenses rise by up to %1 per month — the "
            "same amount you could redirect to savings."
        ),
        "Build a %1 cash buffer": "Build a %1 cash buffer",
        "Your ending balance of %1 is thin relative to monthly outflows. Aim for at least %2 to absorb normal variability.": (
            "Your ending balance of %1 is thin relative to monthly outflows. Aim for at least %2 "
            "to absorb normal variability."
        ),
        "About %1 months of runway": "About %1 months of runway",
        "At the current burn rate, %1 covers roughly %2 months of net cash outflow through the projection period.": (
            "At the current burn rate, %1 covers roughly %2 months of net cash outflow through "
            "the projection period."
        ),
        "%1 %2": "%1 %2",
        "Suggestions": "Suggestions",
        "Based on the saved forecast — the chart above reflects your scenario.": (
            "Based on the saved forecast — the chart above reflects your scenario."
        ),
        "No suggestions for this projection.": "No suggestions for this projection.",
        "Try in scenario": "Try in scenario",
        "Try in scenario: %1": "Try in scenario: %1",
        "Show less": "Show less",
        "Show more": "Show more",
    },
    "fr": {
        "Cut recurring expenses by %1%": "Réduire les dépenses récurrentes de %1%",
        "A uniform %1% reduction across recurring expenses saves about %2 per month and removes the projected cash shortfall.": (
            "Une réduction uniforme de %1% sur les dépenses récurrentes économise environ %2 par "
            "mois et supprime le déficit de trésorerie projeté."
        ),
        "Reduce %1": "Réduire %1",
        "Lowering %1 by %2 per occurrence is enough to avoid the projected cash shortfall if no other cash flows change.": (
            "Réduire %1 de %2 par occurrence suffit à éviter le déficit de trésorerie projeté si "
            "aucun autre flux ne change."
        ),
        "Add %1 recurring income per month": "Ajouter %1 de revenus récurrents par mois",
        "Increasing recurring income by about %1 per month keeps the projection non-negative through the horizon.": (
            "Augmenter les revenus récurrents d'environ %1 par mois maintient la projection "
            "non négative sur l'horizon."
        ),
        "Increase opening balance by %1": "Augmenter le solde d'ouverture de %1",
        "Raising the opening balance by %1 provides enough cushion to stay positive through the projection period.": (
            "Augmenter le solde d'ouverture de %1 offre assez de marge pour rester positif sur "
            "la période de projection."
        ),
        "Consider deferring %1": "Envisager de reporter %1",
        "%1 is scheduled on %2, within 30 days of the projected cash shortfall on %3. Deferring this one-time expense may extend runway.": (
            "%1 est prévu le %2, dans les 30 jours précédant le déficit de trésorerie projeté le "
            "%3. Reporter cette dépense ponctuelle peut prolonger la marge."
        ),
        "Review %1 spending": "Examiner les dépenses %1",
        "%1 averages %2 per month in this projection. Trimming discretionary categories is an easy way to save more.": (
            "%1 représente en moyenne %2 par mois dans cette projection. Réduire les catégories "
            "discrétionnaires est un moyen simple d'épargner davantage."
        ),
        "You could save %1 more per month": "Vous pourriez épargner %1 de plus par mois",
        "The projection stays positive if recurring expenses rise by up to %1 per month — the same amount you could redirect to savings.": (
            "La projection reste positive si les dépenses récurrentes augmentent jusqu'à %1 par "
            "mois — le même montant que vous pourriez orienter vers l'épargne."
        ),
        "Build a %1 cash buffer": "Constituer une réserve de trésorerie de %1",
        "Your ending balance of %1 is thin relative to monthly outflows. Aim for at least %2 to absorb normal variability.": (
            "Votre solde final de %1 est faible par rapport aux sorties mensuelles. Visez au "
            "moins %2 pour absorber la variabilité normale."
        ),
        "About %1 months of runway": "Environ %1 mois de marge",
        "At the current burn rate, %1 covers roughly %2 months of net cash outflow through the projection period.": (
            "Au rythme de consommation actuel, %1 couvre environ %2 mois de sorties nettes de "
            "trésorerie sur la période de projection."
        ),
        "%1 %2": "%1 %2",
        "Suggestions": "Suggestions",
        "Based on the saved forecast — the chart above reflects your scenario.": (
            "Basé sur la prévision enregistrée — le graphique ci-dessus reflète votre scénario."
        ),
        "No suggestions for this projection.": "Aucune suggestion pour cette projection.",
        "Try in scenario": "Essayer en scénario",
        "Try in scenario: %1": "Essayer en scénario : %1",
        "Show less": "Afficher moins",
        "Show more": "Afficher plus",
    },
    "ru": {
        "Cut recurring expenses by %1%": "Сократить повторяющиеся расходы на %1%",
        "A uniform %1% reduction across recurring expenses saves about %2 per month and removes the projected cash shortfall.": (
            "Равномерное сокращение повторяющихся расходов на %1% экономит около %2 в месяц и "
            "устраняет прогнозируемый дефицит денежных средств."
        ),
        "Reduce %1": "Сократить %1",
        "Lowering %1 by %2 per occurrence is enough to avoid the projected cash shortfall if no other cash flows change.": (
            "Снижение %1 на %2 за каждое начисление достаточно, чтобы избежать прогнозируемого "
            "дефицита, если другие потоки не меняются."
        ),
        "Add %1 recurring income per month": "Добавить %1 повторяющегося дохода в месяц",
        "Increasing recurring income by about %1 per month keeps the projection non-negative through the horizon.": (
            "Увеличение повторяющегося дохода примерно на %1 в месяц сохраняет неотрицательный "
            "прогноз на весь горизонт."
        ),
        "Increase opening balance by %1": "Увеличить начальный остаток на %1",
        "Raising the opening balance by %1 provides enough cushion to stay positive through the projection period.": (
            "Повышение начального остатка на %1 даёт достаточный запас, чтобы оставаться в "
            "плюсе на период прогноза."
        ),
        "Consider deferring %1": "Рассмотрите перенос %1",
        "%1 is scheduled on %2, within 30 days of the projected cash shortfall on %3. Deferring this one-time expense may extend runway.": (
            "%1 запланирован на %2, в пределах 30 дней до прогнозируемого дефицита %3. Перенос "
            "этого разового расхода может продлить запас."
        ),
        "Review %1 spending": "Пересмотреть расходы: %1",
        "%1 averages %2 per month in this projection. Trimming discretionary categories is an easy way to save more.": (
            "%1 в среднем составляет %2 в месяц в этом прогнозе. Сокращение дискреционных "
            "категорий — простой способ сэкономить больше."
        ),
        "You could save %1 more per month": "Вы могли бы сэкономить ещё %1 в месяц",
        "The projection stays positive if recurring expenses rise by up to %1 per month — the same amount you could redirect to savings.": (
            "Прогноз остаётся положительным, если повторяющиеся расходы вырастут до %1 в месяц — "
            "ту же сумму можно направить на сбережения."
        ),
        "Build a %1 cash buffer": "Создать денежный резерв %1",
        "Your ending balance of %1 is thin relative to monthly outflows. Aim for at least %2 to absorb normal variability.": (
            "Ваш конечный остаток %1 мал относительно месячных оттоков. Стремитесь как минимум "
            "к %2, чтобы поглощать обычные колебания."
        ),
        "About %1 months of runway": "Около %1 месяцев запаса",
        "At the current burn rate, %1 covers roughly %2 months of net cash outflow through the projection period.": (
            "При текущем темпе расходования %1 покрывает примерно %2 месяцев чистого оттока "
            "денежных средств на период прогноза."
        ),
        "%1 %2": "%1 %2",
        "Suggestions": "Рекомендации",
        "Based on the saved forecast — the chart above reflects your scenario.": (
            "На основе сохранённого прогноза — график выше отражает ваш сценарий."
        ),
        "No suggestions for this projection.": "Нет рекомендаций для этого прогноза.",
        "Try in scenario": "Попробовать в сценарии",
        "Try in scenario: %1": "Попробовать в сценарии: %1",
        "Show less": "Показать меньше",
        "Show more": "Показать больше",
    },
    "es": {
        "Cut recurring expenses by %1%": "Reducir los gastos recurrentes un %1%",
        "A uniform %1% reduction across recurring expenses saves about %2 per month and removes the projected cash shortfall.": (
            "Una reducción uniforme del %1% en los gastos recurrentes ahorra unos %2 al mes y "
            "elimina el déficit de caja previsto."
        ),
        "Reduce %1": "Reducir %1",
        "Lowering %1 by %2 per occurrence is enough to avoid the projected cash shortfall if no other cash flows change.": (
            "Reducir %1 en %2 por ocurrencia basta para evitar el déficit de caja previsto si "
            "no cambian otros flujos."
        ),
        "Add %1 recurring income per month": "Añadir %1 de ingresos recurrentes al mes",
        "Increasing recurring income by about %1 per month keeps the projection non-negative through the horizon.": (
            "Aumentar los ingresos recurrentes unos %1 al mes mantiene la proyección no negativa "
            "en todo el horizonte."
        ),
        "Increase opening balance by %1": "Aumentar el saldo inicial en %1",
        "Raising the opening balance by %1 provides enough cushion to stay positive through the projection period.": (
            "Subir el saldo inicial en %1 aporta margen suficiente para mantenerse positivo "
            "durante el período de proyección."
        ),
        "Consider deferring %1": "Considerar aplazar %1",
        "%1 is scheduled on %2, within 30 days of the projected cash shortfall on %3. Deferring this one-time expense may extend runway.": (
            "%1 está programado el %2, dentro de los 30 días previos al déficit de caja previsto "
            "el %3. Aplazar este gasto puntual puede ampliar el margen."
        ),
        "Review %1 spending": "Revisar el gasto en %1",
        "%1 averages %2 per month in this projection. Trimming discretionary categories is an easy way to save more.": (
            "%1 promedia %2 al mes en esta proyección. Recortar categorías discrecionales es una "
            "forma sencilla de ahorrar más."
        ),
        "You could save %1 more per month": "Podría ahorrar %1 más al mes",
        "The projection stays positive if recurring expenses rise by up to %1 per month — the same amount you could redirect to savings.": (
            "La proyección se mantiene positiva si los gastos recurrentes suben hasta %1 al mes — "
            "la misma cantidad que podría destinar al ahorro."
        ),
        "Build a %1 cash buffer": "Crear un colchón de caja de %1",
        "Your ending balance of %1 is thin relative to monthly outflows. Aim for at least %2 to absorb normal variability.": (
            "Su saldo final de %1 es escaso respecto a las salidas mensuales. Apunte al menos a "
            "%2 para absorber la variabilidad normal."
        ),
        "About %1 months of runway": "Unos %1 meses de margen",
        "At the current burn rate, %1 covers roughly %2 months of net cash outflow through the projection period.": (
            "Al ritmo de consumo actual, %1 cubre aproximadamente %2 meses de salida neta de "
            "caja en el período de proyección."
        ),
        "%1 %2": "%1 %2",
        "Suggestions": "Sugerencias",
        "Based on the saved forecast — the chart above reflects your scenario.": (
            "Según el pronóstico guardado — el gráfico anterior refleja su escenario."
        ),
        "No suggestions for this projection.": "No hay sugerencias para esta proyección.",
        "Try in scenario": "Probar en escenario",
        "Try in scenario: %1": "Probar en escenario: %1",
        "Show less": "Mostrar menos",
        "Show more": "Mostrar más",
    },
    "de": {
        "Cut recurring expenses by %1%": "Wiederkehrende Ausgaben um %1% kürzen",
        "A uniform %1% reduction across recurring expenses saves about %2 per month and removes the projected cash shortfall.": (
            "Eine einheitliche Kürzung wiederkehrender Ausgaben um %1% spart etwa %2 pro Monat "
            "und beseitigt die prognostizierte Liquiditätslücke."
        ),
        "Reduce %1": "%1 reduzieren",
        "Lowering %1 by %2 per occurrence is enough to avoid the projected cash shortfall if no other cash flows change.": (
            "Eine Senkung von %1 um %2 pro Vorkommen reicht aus, die prognostizierte "
            "Liquiditätslücke zu vermeiden, wenn sich sonst nichts ändert."
        ),
        "Add %1 recurring income per month": "%1 wiederkehrendes Einkommen pro Monat hinzufügen",
        "Increasing recurring income by about %1 per month keeps the projection non-negative through the horizon.": (
            "Eine Erhöhung des wiederkehrenden Einkommens um etwa %1 pro Monat hält die "
            "Prognose über den Horizont hinweg nicht negativ."
        ),
        "Increase opening balance by %1": "Anfangssaldo um %1 erhöhen",
        "Raising the opening balance by %1 provides enough cushion to stay positive through the projection period.": (
            "Eine Erhöhung des Anfangssaldos um %1 bietet genug Puffer, um im Prognosezeitraum "
            "positiv zu bleiben."
        ),
        "Consider deferring %1": "Verschieben von %1 erwägen",
        "%1 is scheduled on %2, within 30 days of the projected cash shortfall on %3. Deferring this one-time expense may extend runway.": (
            "%1 ist am %2 fällig, innerhalb von 30 Tagen vor der prognostizierten "
            "Liquiditätslücke am %3. Das Verschieben dieser einmaligen Ausgabe kann die "
            "Reichweite verlängern."
        ),
        "Review %1 spending": "Ausgaben für %1 prüfen",
        "%1 averages %2 per month in this projection. Trimming discretionary categories is an easy way to save more.": (
            "%1 beträgt in dieser Prognose durchschnittlich %2 pro Monat. Optionale "
            "Kategorien zu kürzen ist ein einfacher Weg, mehr zu sparen."
        ),
        "You could save %1 more per month": "Sie könnten %1 mehr pro Monat sparen",
        "The projection stays positive if recurring expenses rise by up to %1 per month — the same amount you could redirect to savings.": (
            "Die Prognose bleibt positiv, wenn wiederkehrende Ausgaben um bis zu %1 pro Monat "
            "steigen — derselbe Betrag, den Sie zum Sparen nutzen könnten."
        ),
        "Build a %1 cash buffer": "Einen Liquiditätspuffer von %1 aufbauen",
        "Your ending balance of %1 is thin relative to monthly outflows. Aim for at least %2 to absorb normal variability.": (
            "Ihr Endsaldo von %1 ist im Verhältnis zu den monatlichen Abflüssen gering. "
            "Streben Sie mindestens %2 an, um normale Schwankungen abzufedern."
        ),
        "About %1 months of runway": "Etwa %1 Monate Reichweite",
        "At the current burn rate, %1 covers roughly %2 months of net cash outflow through the projection period.": (
            "Bei der aktuellen Verbrauchsrate deckt %1 ungefähr %2 Monate netto "
            "Cash-Abfluss im Prognosezeitraum."
        ),
        "%1 %2": "%1 %2",
        "Suggestions": "Vorschläge",
        "Based on the saved forecast — the chart above reflects your scenario.": (
            "Basierend auf der gespeicherten Prognose — die Grafik oben zeigt Ihr Szenario."
        ),
        "No suggestions for this projection.": "Keine Vorschläge für diese Prognose.",
        "Try in scenario": "Im Szenario testen",
        "Try in scenario: %1": "Im Szenario testen: %1",
        "Show less": "Weniger anzeigen",
        "Show more": "Mehr anzeigen",
    },
}


def _escape_xml(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def apply_translations(locale: str) -> None:
    path = I18N_DIR / f"app_{locale}.ts"
    content = path.read_text(encoding="utf-8")
    mapping = TRANSLATIONS[locale]

    for source, translation in mapping.items():
        escaped_source = re.escape(source)
        escaped_translation = _escape_xml(translation)
        pattern = (
            rf"(<source>{escaped_source}</source>\s*)"
            rf"<translation(?: type=\"unfinished\")?>(?:[^<]*)</translation>"
        )
        replacement = rf"\1<translation>{escaped_translation}</translation>"
        content, count = re.subn(pattern, replacement, content)
        if count == 0:
            msg = f"Missing translation entry for {locale!r}: {source!r}"
            raise RuntimeError(msg)

    path.write_text(content, encoding="utf-8")


def main() -> None:
    for locale in ("en", "fr", "ru", "es", "de"):
        apply_translations(locale)
        print(f"Updated app_{locale}.ts")


if __name__ == "__main__":
    main()
