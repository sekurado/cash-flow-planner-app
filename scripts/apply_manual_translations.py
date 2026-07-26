#!/usr/bin/env python3
"""Apply manual_translations.json entries to Qt .ts files."""

from __future__ import annotations

import json
import re
import sys
import xml.sax.saxutils as saxutils
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TRANSLATIONS_PATH = ROOT / "i18n" / "manual_translations.json"
LOCALES = ("fr", "ru", "es", "de")

_SETTINGS_SOURCES = {
    "User manual",
    "Open the bundled PDF guide in your system's default viewer",
    "Open ▶",
    "Open user manual",
}


def _normalize_source(text: str) -> str:
    return (
        text.replace("&apos;", "'")
        .replace("&quot;", '"')
        .replace("&amp;", "&")
        .replace("&lt;", "<")
        .replace("&gt;", ">")
    )


def _load_translations() -> dict[str, dict[str, str]]:
    raw = json.loads(TRANSLATIONS_PATH.read_text(encoding="utf-8"))
    normalized: dict[str, dict[str, str]] = {}
    extra_errors = {
        "fr": {
            "User manual is not available.": "Le manuel utilisateur n'est pas disponible.",
            "Could not open the user manual.": "Impossible d'ouvrir le manuel utilisateur.",
        },
        "ru": {
            "User manual is not available.": "Руководство пользователя недоступно.",
            "Could not open the user manual.": "Не удалось открыть руководство пользователя.",
        },
        "es": {
            "User manual is not available.": "El manual de usuario no está disponible.",
            "Could not open the user manual.": "No se pudo abrir el manual de usuario.",
        },
        "de": {
            "User manual is not available.": "Das Benutzerhandbuch ist nicht verfügbar.",
            "Could not open the user manual.": "Das Benutzerhandbuch konnte nicht geöffnet werden.",
        },
    }
    settings_extra = {
        "fr": {
            "Open the bundled PDF guide in your system's default viewer": (
                "Ouvrez le guide PDF intégré dans votre visionneuse système par défaut"
            ),
        },
        "ru": {
            "Open the bundled PDF guide in your system's default viewer": (
                "Откройте встроенное PDF-руководство в системной программе просмотра"
            ),
        },
        "es": {
            "Open the bundled PDF guide in your system's default viewer": (
                "Abra la guía PDF incluida en el visor predeterminado del sistema"
            ),
        },
        "de": {
            "Open the bundled PDF guide in your system's default viewer": (
                "Öffnen Sie das gebündelte PDF-Handbuch im Standard-PDF-Viewer des Systems"
            ),
        },
    }
    for locale, mapping in raw.items():
        locale_map: dict[str, str] = {}
        for source, translation in mapping.items():
            locale_map[_normalize_source(source)] = translation
        locale_map.update(extra_errors.get(locale, {}))
        locale_map.update(settings_extra.get(locale, {}))
        normalized[locale] = locale_map
    return normalized


def _escape_xml(text: str) -> str:
    return saxutils.escape(text, entities={"'": "&apos;", '"': "&quot;"})


def _apply_to_context(block: str, translations: dict[str, str]) -> tuple[str, int]:
    updated = 0

    def replace_message(match: re.Match[str]) -> str:
        nonlocal updated
        message = match.group(0)
        source_match = re.search(r"<source>(.*?)</source>", message, re.S)
        if source_match is None:
            return message
        source = _normalize_source(source_match.group(1))
        translation = translations.get(source)
        if translation is None:
            return message
        escaped = _escape_xml(translation)
        new_message = re.sub(
            r"<translation[^>]*>.*?</translation>",
            f"<translation>{escaped}</translation>",
            message,
            count=1,
            flags=re.S,
        )
        if new_message != message:
            updated += 1
        return new_message

    pattern = re.compile(r"<message>.*?</message>", re.S)
    return pattern.sub(replace_message, block), updated


def apply_locale(locale: str, translations: dict[str, dict[str, str]]) -> int:
    ts_path = ROOT / "i18n" / f"app_{locale}.ts"
    text = ts_path.read_text(encoding="utf-8")
    locale_map = translations[locale]
    total = 0

    for context_name in ("UserManual", "SettingsPage", "AppErrors"):
        context_pattern = re.compile(
            rf"(<context>\s*<name>{context_name}</name>)(.*?)(</context>)",
            re.S,
        )

        def replace_context(match: re.Match[str]) -> str:
            nonlocal total
            header, body, footer = match.groups()
            if context_name == "AppErrors":
                sources = {
                    "User manual is not available.",
                    "Could not open the user manual.",
                }
                filtered = {k: v for k, v in locale_map.items() if k in sources}
            elif context_name == "SettingsPage":
                filtered = {k: v for k, v in locale_map.items() if k in _SETTINGS_SOURCES}
            else:
                filtered = locale_map
            new_body, count = _apply_to_context(body, filtered)
            total += count
            return header + new_body + footer

        text = context_pattern.sub(replace_context, text)

    ts_path.write_text(text, encoding="utf-8")
    return total


def main() -> int:
    translations = _load_translations()
    for locale in LOCALES:
        count = apply_locale(locale, translations)
        print(f"Updated {count} messages in app_{locale}.ts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
