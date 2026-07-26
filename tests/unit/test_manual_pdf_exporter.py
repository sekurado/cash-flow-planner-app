from __future__ import annotations

from pathlib import Path

import pytest
from PySide6.QtCore import QTranslator
from PySide6.QtWidgets import QApplication
from reportlab.platypus import Paragraph, Table  # type: ignore[import-untyped]

from src.app.i18n.manual_content import manual_chapters
from src.export.manual_pdf_exporter import (
    ManualPdfExporter,
    build_manual_story,
    pdf_contains_text,
    pdf_has_chapter_outlines,
    pdf_page_count,
)


def _story_plain_text(story: list[object]) -> str:
    parts: list[str] = []

    def _collect(flowable: object) -> None:
        if isinstance(flowable, Paragraph):
            parts.append(flowable.getPlainText())
            return
        if isinstance(flowable, Table):
            for row in flowable._cellvalues:
                for cell in row:
                    if isinstance(cell, Paragraph):
                        parts.append(cell.getPlainText())
                    elif isinstance(cell, Table):
                        _collect(cell)
                    elif isinstance(cell, str):
                        parts.append(cell)

    for flowable in story:
        _collect(flowable)

    return " ".join(parts)


@pytest.mark.unit
def test_build_manual_story_includes_cover_toc_and_chapters(qt_app: QApplication) -> None:
    del qt_app
    chapters = manual_chapters()
    story = build_manual_story(chapters)
    paragraph_text = _story_plain_text(story)

    assert "Manual version: 1.0" in paragraph_text
    assert "Table of Contents" in paragraph_text
    assert "Welcome" in paragraph_text
    assert "Date pattern cheat sheet" in paragraph_text
    assert "Tip:" in paragraph_text
    assert "Note:" in paragraph_text
    assert "Important:" in paragraph_text


@pytest.mark.unit
def test_manual_pdf_export_creates_multi_page_document(
    qt_app: QApplication,
    tmp_path: Path,
) -> None:
    del qt_app
    output = tmp_path / "manual.pdf"
    chapters = manual_chapters()

    ManualPdfExporter().export(output, chapters=chapters)

    assert output.exists()
    assert output.stat().st_size > 0
    page_count = pdf_page_count(output)
    assert page_count >= len(chapters) + 2
    assert pdf_contains_text(output, "Welcome")
    assert pdf_contains_text(output, "Cash shortfall alert")
    assert pdf_has_chapter_outlines(
        output,
        [chapter.title for chapter in chapters],
    )


_LOCALE_WELCOME_TITLES = {
    "en": "Welcome",
    "fr": "Bienvenue",
    "ru": "Добро пожаловать",
    "es": "Bienvenida",
    "de": "Willkommen",
}


def _install_locale_translator(qt_app: QApplication, locale: str) -> QTranslator | None:
    if locale == "en":
        return None

    import src.app.resources_rc  # noqa: F401

    translator = QTranslator()
    assert translator.load(f":/i18n/app_{locale}.qm")
    qt_app.installTranslator(translator)
    return translator


@pytest.mark.unit
@pytest.mark.parametrize("locale", ["en", "fr", "ru", "es", "de"])
def test_manual_pdf_export_uses_translated_chapter_titles(
    qt_app: QApplication,
    tmp_path: Path,
    locale: str,
) -> None:
    translator = _install_locale_translator(qt_app, locale)
    try:
        output = tmp_path / f"manual_{locale}.pdf"
        chapters = manual_chapters()
        expected_title = _LOCALE_WELCOME_TITLES[locale]

        assert chapters[0].title == expected_title
        assert expected_title != _LOCALE_WELCOME_TITLES["en"] or locale == "en"

        ManualPdfExporter().export(output, locale=locale)

        assert output.stat().st_size > 0
        page_count = pdf_page_count(output)
        assert page_count >= len(chapters) + 2

        if locale == "en":
            assert pdf_contains_text(output, expected_title)
            assert pdf_has_chapter_outlines(output, [chapter.title for chapter in chapters])
        elif locale != "ru":
            assert pdf_contains_text(output, expected_title)
    finally:
        if translator is not None:
            qt_app.removeTranslator(translator)
