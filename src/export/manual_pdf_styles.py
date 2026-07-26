from __future__ import annotations

from reportlab.lib import colors  # type: ignore[import-untyped]
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT  # type: ignore[import-untyped]
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet  # type: ignore[import-untyped]
from reportlab.lib.units import cm  # type: ignore[import-untyped]

from src.export.pdf_colors import INCOME_GREEN, PRIMARY
from src.export.pdf_fonts import pdf_font_name

FONT_NAME = pdf_font_name()
PAGE_MARGIN = 2 * cm

CALLOUT_TIP_BORDER = INCOME_GREEN
CALLOUT_TIP_BG = colors.HexColor("#ECFDF5")
CALLOUT_NOTE_BORDER = PRIMARY
CALLOUT_NOTE_BG = colors.HexColor("#EEF2FF")
CALLOUT_IMPORTANT_BORDER = colors.HexColor("#F59E0B")
CALLOUT_IMPORTANT_BG = colors.HexColor("#FFFBEB")

STYLE_CHAPTER_TITLE = "ManualChapterTitle"
STYLE_SECTION_HEADING = "ManualSectionHeading"
STYLE_BODY_TEXT = "ManualBodyText"
STYLE_COVER_META = "ManualCoverMeta"
STYLE_TOC_HEADING = "ManualTocHeading"
STYLE_TOC_LEVEL0 = "ManualTocLevel0"
STYLE_TOC_LEVEL1 = "ManualTocLevel1"
STYLE_CALLOUT_BODY = "ManualCalloutBody"

CALLOUT_LABEL_TIP = "Tip:"
CALLOUT_LABEL_NOTE = "Note:"
CALLOUT_LABEL_IMPORTANT = "Important:"
TOC_HEADING = "Table of Contents"
PATTERN_TABLE_HEADERS = ("Pattern", "Meaning")


def build_manual_styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        STYLE_CHAPTER_TITLE: ParagraphStyle(
            name=STYLE_CHAPTER_TITLE,
            parent=base["Heading1"],
            fontName=FONT_NAME,
            fontSize=20,
            leading=24,
            textColor=PRIMARY,
            spaceBefore=24,
            spaceAfter=12,
        ),
        STYLE_SECTION_HEADING: ParagraphStyle(
            name=STYLE_SECTION_HEADING,
            parent=base["Heading2"],
            fontName=FONT_NAME,
            fontSize=14,
            leading=18,
            textColor=colors.HexColor("#0F172A"),
            spaceBefore=14,
            spaceAfter=8,
            borderPadding=2,
            borderWidth=0,
            borderColor=colors.HexColor("#E2E8F0"),
        ),
        STYLE_BODY_TEXT: ParagraphStyle(
            name=STYLE_BODY_TEXT,
            parent=base["Normal"],
            fontName=FONT_NAME,
            fontSize=10.5,
            leading=14,
            alignment=TA_LEFT,
            spaceAfter=8,
        ),
        STYLE_COVER_META: ParagraphStyle(
            name=STYLE_COVER_META,
            parent=base["Normal"],
            fontName=FONT_NAME,
            fontSize=11,
            leading=14,
            textColor=colors.HexColor("#475569"),
            alignment=TA_LEFT,
            spaceAfter=6,
        ),
        STYLE_TOC_HEADING: ParagraphStyle(
            name=STYLE_TOC_HEADING,
            parent=base["Heading1"],
            fontName=FONT_NAME,
            fontSize=18,
            leading=22,
            textColor=PRIMARY,
            spaceAfter=12,
        ),
        STYLE_TOC_LEVEL0: ParagraphStyle(
            name=STYLE_TOC_LEVEL0,
            parent=base["Normal"],
            fontName=FONT_NAME,
            fontSize=12,
            leading=16,
            leftIndent=0,
            spaceAfter=4,
        ),
        STYLE_TOC_LEVEL1: ParagraphStyle(
            name=STYLE_TOC_LEVEL1,
            parent=base["Normal"],
            fontName=FONT_NAME,
            fontSize=10,
            leading=14,
            leftIndent=16,
            spaceAfter=2,
        ),
        STYLE_CALLOUT_BODY: ParagraphStyle(
            name=STYLE_CALLOUT_BODY,
            parent=base["Normal"],
            fontName=FONT_NAME,
            fontSize=10,
            leading=13,
            alignment=TA_JUSTIFY,
            spaceAfter=0,
        ),
    }


def mono_span(text: str) -> str:
    escaped = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return f'<font face="Courier">{escaped}</font>'
