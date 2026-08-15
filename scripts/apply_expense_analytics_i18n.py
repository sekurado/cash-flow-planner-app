#!/usr/bin/env python3
"""Apply Spending analytics QML translations to .ts files."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
I18N_DIR = ROOT / "i18n"

TRANSLATIONS: dict[str, dict[str, str]] = {
    "en": {
        "Overview": "Overview",
        "Top categories": "Top categories",
        "No category spending in this period.": "No category spending in this period.",
        "Top places": "Top places",
        "No place spending in this period.": "No place spending in this period.",
        "Top names": "Top names",
        "No name spending in this period.": "No name spending in this period.",
        "No spending in this period.": "No spending in this period.",
        "Other": "Other",
        "Amount (%1)": "Amount (%1)",
        "Search name, category, place, or note": "Search name, category, place, or note",
        "Search expenses": "Search expenses",
        "This month": "This month",
        "Last 30 days": "Last 30 days",
        "Year to date": "Year to date",
        "Custom": "Custom",
        "Apply": "Apply",
        "Clear filters": "Clear filters",
        "Spending": "Spending",
        "No matching expenses": "No matching expenses",
        "Try a different search term or clear filters.": (
            "Try a different search term or clear filters."
        ),
        "No recorded expenses yet": "No recorded expenses yet",
        "Add your first recorded expense using the + button": (
            "Add your first recorded expense using the + button"
        ),
        "Try adjusting your search or date range, or clear filters.": (
            "Try adjusting your search or date range, or clear filters."
        ),
        "Add recorded expense": "Add recorded expense",
        "Delete recorded expense": "Delete recorded expense",
    },
    "fr": {
        "Overview": "Aperçu",
        "Top categories": "Principales catégories",
        "No category spending in this period.": "Aucune dépense par catégorie sur cette période.",
        "Top places": "Principaux lieux",
        "No place spending in this period.": "Aucune dépense par lieu sur cette période.",
        "Top names": "Principaux libellés",
        "No name spending in this period.": "Aucune dépense par libellé sur cette période.",
        "No spending in this period.": "Aucune dépense sur cette période.",
        "Other": "Autre",
        "Amount (%1)": "Montant (%1)",
        "Search name, category, place, or note": (
            "Rechercher un libellé, une catégorie, un lieu ou une note"
        ),
        "Search expenses": "Rechercher des dépenses",
        "This month": "Ce mois-ci",
        "Last 30 days": "30 derniers jours",
        "Year to date": "Depuis le début de l'année",
        "Custom": "Personnalisé",
        "Apply": "Appliquer",
        "Clear filters": "Effacer les filtres",
        "Spending": "Dépenses",
        "No matching expenses": "Aucune dépense correspondante",
        "Try a different search term or clear filters.": (
            "Essayez un autre terme de recherche ou effacez les filtres."
        ),
        "No recorded expenses yet": "Aucune dépense enregistrée",
        "Add your first recorded expense using the + button": (
            "Ajoutez votre première dépense enregistrée avec le bouton +"
        ),
        "Try adjusting your search or date range, or clear filters.": (
            "Modifiez votre recherche ou la plage de dates, ou effacez les filtres."
        ),
        "Add recorded expense": "Ajouter une dépense enregistrée",
        "Delete recorded expense": "Supprimer la dépense enregistrée",
    },
    "ru": {
        "Overview": "Обзор",
        "Top categories": "Основные категории",
        "No category spending in this period.": "Нет расходов по категориям за этот период.",
        "Top places": "Основные места",
        "No place spending in this period.": "Нет расходов по местам за этот период.",
        "Top names": "Основные наименования",
        "No name spending in this period.": "Нет расходов по наименованиям за этот период.",
        "No spending in this period.": "Нет расходов за этот период.",
        "Other": "Прочее",
        "Amount (%1)": "Сумма (%1)",
        "Search name, category, place, or note": (
            "Поиск по наименованию, категории, месту или заметке"
        ),
        "Search expenses": "Поиск расходов",
        "This month": "Этот месяц",
        "Last 30 days": "Последние 30 дней",
        "Year to date": "С начала года",
        "Custom": "Произвольный",
        "Apply": "Применить",
        "Clear filters": "Сбросить фильтры",
        "Spending": "Расходы",
        "No matching expenses": "Нет подходящих расходов",
        "Try a different search term or clear filters.": (
            "Попробуйте другой поисковый запрос или сбросьте фильтры."
        ),
        "No recorded expenses yet": "Пока нет записанных расходов",
        "Add your first recorded expense using the + button": (
            "Добавьте первый расход с помощью кнопки +"
        ),
        "Try adjusting your search or date range, or clear filters.": (
            "Измените поиск или диапазон дат либо сбросьте фильтры."
        ),
        "Add recorded expense": "Добавить расход",
        "Delete recorded expense": "Удалить расход",
    },
    "es": {
        "Overview": "Resumen",
        "Top categories": "Principales categorías",
        "No category spending in this period.": "No hay gastos por categoría en este período.",
        "Top places": "Principales lugares",
        "No place spending in this period.": "No hay gastos por lugar en este período.",
        "Top names": "Principales nombres",
        "No name spending in this period.": "No hay gastos por nombre en este período.",
        "No spending in this period.": "No hay gastos en este período.",
        "Other": "Otros",
        "Amount (%1)": "Importe (%1)",
        "Search name, category, place, or note": ("Buscar nombre, categoría, lugar o nota"),
        "Search expenses": "Buscar gastos",
        "This month": "Este mes",
        "Last 30 days": "Últimos 30 días",
        "Year to date": "Año en curso",
        "Custom": "Personalizado",
        "Apply": "Aplicar",
        "Clear filters": "Borrar filtros",
        "Spending": "Gastos",
        "No matching expenses": "No hay gastos coincidentes",
        "Try a different search term or clear filters.": (
            "Pruebe otro término de búsqueda o borre los filtros."
        ),
        "No recorded expenses yet": "Aún no hay gastos registrados",
        "Add your first recorded expense using the + button": (
            "Añada su primer gasto registrado con el botón +"
        ),
        "Try adjusting your search or date range, or clear filters.": (
            "Ajuste la búsqueda o el rango de fechas, o borre los filtros."
        ),
        "Add recorded expense": "Añadir gasto registrado",
        "Delete recorded expense": "Eliminar gasto registrado",
    },
    "de": {
        "Overview": "Übersicht",
        "Top categories": "Top-Kategorien",
        "No category spending in this period.": "Keine Ausgaben nach Kategorie in diesem Zeitraum.",
        "Top places": "Top-Orte",
        "No place spending in this period.": "Keine Ausgaben nach Ort in diesem Zeitraum.",
        "Top names": "Top-Bezeichnungen",
        "No name spending in this period.": "Keine Ausgaben nach Bezeichnung in diesem Zeitraum.",
        "No spending in this period.": "Keine Ausgaben in diesem Zeitraum.",
        "Other": "Sonstige",
        "Amount (%1)": "Betrag (%1)",
        "Search name, category, place, or note": ("Name, Kategorie, Ort oder Notiz suchen"),
        "Search expenses": "Ausgaben suchen",
        "This month": "Dieser Monat",
        "Last 30 days": "Letzte 30 Tage",
        "Year to date": "Seit Jahresbeginn",
        "Custom": "Benutzerdefiniert",
        "Apply": "Anwenden",
        "Clear filters": "Filter zurücksetzen",
        "Spending": "Ausgaben",
        "No matching expenses": "Keine passenden Ausgaben",
        "Try a different search term or clear filters.": (
            "Versuchen Sie einen anderen Suchbegriff oder setzen Sie die Filter zurück."
        ),
        "No recorded expenses yet": "Noch keine erfassten Ausgaben",
        "Add your first recorded expense using the + button": (
            "Fügen Sie Ihre erste erfasste Ausgabe mit der Schaltfläche + hinzu"
        ),
        "Try adjusting your search or date range, or clear filters.": (
            "Passen Sie Suche oder Datumsbereich an oder setzen Sie die Filter zurück."
        ),
        "Add recorded expense": "Erfasste Ausgabe hinzufügen",
        "Delete recorded expense": "Erfasste Ausgabe löschen",
    },
}


def _escape_xml(text: str) -> str:
    return (
        text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
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
    for locale in TRANSLATIONS:
        apply_translations(locale)
        print(f"Updated app_{locale}.ts")


if __name__ == "__main__":
    main()
