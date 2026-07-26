from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from src.app.i18n.manual_content import (
    MANUAL_VERSION,
    ManualBlock,
    ManualBlockType,
    ManualChapter,
    manual_chapters,
    manual_subtitle,
    manual_title,
)


def _all_section_blocks() -> list[tuple[str, str, tuple[ManualBlock, ...]]]:
    return [
        (chapter.title, section.heading, section.blocks)
        for chapter in manual_chapters()
        for section in chapter.sections
    ]


def _chapter_text(chapter: ManualChapter) -> str:
    parts: list[str] = [chapter.title]
    for section in chapter.sections:
        parts.append(section.heading)
        for block in section.blocks:
            parts.append(block.text)
            if block.title:
                parts.append(block.title)
    return " ".join(parts).lower()


@pytest.mark.unit
def test_manual_version_constant() -> None:
    assert MANUAL_VERSION == "1.0"


@pytest.mark.unit
def test_manual_title_and_subtitle() -> None:
    assert manual_title() == "Cash Flow Planner"
    assert manual_subtitle() == "User Manual"


@pytest.mark.unit
def test_manual_chapter_count_and_order() -> None:
    chapters = manual_chapters()
    assert len(chapters) == 8
    assert [chapter.title for chapter in chapters] == [
        "Welcome",
        "Getting started",
        "Cash flows",
        "Running a projection",
        "What-if scenarios",
        "Import & export",
        "Settings & preferences",
        "Quick reference",
    ]


@pytest.mark.unit
def test_every_chapter_has_sections_with_blocks() -> None:
    chapters = manual_chapters()
    for chapter in chapters:
        assert len(chapter.sections) >= 1
        for section in chapter.sections:
            assert section.heading
            assert len(section.blocks) >= 1
            for block in section.blocks:
                assert block.text
                assert block.block_type in ManualBlockType


@pytest.mark.unit
def test_manual_section_headings_match_outline() -> None:
    chapters = manual_chapters()
    section_headings = [section.heading for chapter in chapters for section in chapter.sections]
    assert section_headings == [
        "About Cash Flow Planner",
        "Who this manual is for",
        "First launch",
        "Create a forecast",
        "Start from a template",
        "Add income and expenses",
        "Date patterns",
        "Edit and delete",
        "Set horizon and opening balance",
        "Read the monthly table",
        "Balance chart",
        "Cash shortfall alert",
        "Enable overrides",
        "Compare with baseline",
        "Import CSV/Excel",
        "Export executive PDF",
        "Share .ftplan files",
        "Theme and language",
        "Exchange rates",
        "Methodology",
        "Date pattern cheat sheet",
        "Tips and shortcuts",
    ]


@pytest.mark.unit
def test_manual_supports_all_block_types() -> None:
    block_types = {
        block.block_type
        for chapter in manual_chapters()
        for section in chapter.sections
        for block in section.blocks
    }
    assert ManualBlockType.PARAGRAPH in block_types
    assert ManualBlockType.BULLET_LIST in block_types
    assert ManualBlockType.TIP in block_types
    assert ManualBlockType.NOTE in block_types
    assert ManualBlockType.IMPORTANT in block_types
    assert ManualBlockType.PATTERN_TABLE in block_types


@pytest.mark.unit
def test_manual_has_no_placeholder_markers() -> None:
    combined = " ".join(
        block.text for _chapter, _section, blocks in _all_section_blocks() for block in blocks
    ).lower()
    assert "todo" not in combined
    assert "lorem" not in combined
    assert "placeholder" not in combined


@pytest.mark.unit
def test_manual_english_strings_use_glossary_terms() -> None:
    combined = " ".join(_chapter_text(chapter) for chapter in manual_chapters())
    assert "forecast" in combined
    assert "cash flow" in combined
    assert "cash shortfall" in combined
    assert "scenario" in combined
    assert "plan_id" not in combined
    assert "entry" not in combined.replace("history", "")


@pytest.mark.unit
def test_each_section_has_substantive_body_content() -> None:
    for _chapter_title, _section_heading, blocks in _all_section_blocks():
        paragraphs = sum(1 for block in blocks if block.block_type is ManualBlockType.PARAGRAPH)
        bullet_lists = sum(1 for block in blocks if block.block_type is ManualBlockType.BULLET_LIST)
        pattern_tables = sum(
            1 for block in blocks if block.block_type is ManualBlockType.PATTERN_TABLE
        )
        assert paragraphs >= 2 or (paragraphs >= 1 and (bullet_lists >= 1 or pattern_tables >= 1))


@pytest.mark.unit
def test_major_chapters_include_tips_and_important_callouts() -> None:
    chapters = manual_chapters()
    for chapter in chapters:
        tips = 0
        important = 0
        for section in chapter.sections:
            for block in section.blocks:
                if block.block_type is ManualBlockType.TIP:
                    tips += 1
                if block.block_type is ManualBlockType.IMPORTANT:
                    important += 1
        assert tips >= 2, chapter.title
        assert important >= 1, chapter.title


@pytest.mark.unit
def test_pattern_cheat_sheet_includes_four_literals() -> None:
    pattern_blocks = [
        block
        for _chapter, _section, blocks in _all_section_blocks()
        for block in blocks
        if block.block_type is ManualBlockType.PATTERN_TABLE
    ]
    assert len(pattern_blocks) == 1
    rows = [line for line in pattern_blocks[0].text.split("\n") if line.strip()]
    assert len(rows) == 4
    assert rows[0].startswith("...\t")
    assert "10..\t" in rows[1]
    assert "15.03.\t" in rows[2]
    assert "15.03.2026\t" in rows[3]


@pytest.mark.unit
def test_manual_french_translations(qt_app: QApplication) -> None:
    from PySide6.QtCore import QTranslator

    import src.app.resources_rc  # noqa: F401

    translator = QTranslator()
    assert translator.load(":/i18n/app_fr.qm")
    qt_app.installTranslator(translator)

    try:
        chapters = manual_chapters()
        assert chapters[0].title == "Bienvenue"
        assert chapters[2].title == "Flux de trésorerie"
        assert manual_subtitle() == "Manuel utilisateur"
    finally:
        qt_app.removeTranslator(translator)
