from __future__ import annotations

import re
from collections.abc import Callable, Sequence
from datetime import UTC, datetime
from pathlib import Path

from reportlab.lib import colors  # type: ignore[import-untyped]
from reportlab.lib.pagesizes import letter  # type: ignore[import-untyped]
from reportlab.lib.styles import ParagraphStyle  # type: ignore[import-untyped]
from reportlab.lib.units import inch  # type: ignore[import-untyped]
from reportlab.platypus import (  # type: ignore[import-untyped]
    Flowable,
    HRFlowable,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.platypus.tableofcontents import TableOfContents  # type: ignore[import-untyped]

from src.app.i18n.manual_content import (
    MANUAL_VERSION,
    ManualBlock,
    ManualBlockType,
    ManualChapter,
    manual_chapters,
    manual_subtitle,
    manual_title,
)
from src.domain.exceptions import ExportError
from src.export._atomic import atomic_write
from src.export.manual_pdf_styles import (
    CALLOUT_IMPORTANT_BG,
    CALLOUT_IMPORTANT_BORDER,
    CALLOUT_LABEL_IMPORTANT,
    CALLOUT_LABEL_NOTE,
    CALLOUT_LABEL_TIP,
    CALLOUT_NOTE_BG,
    CALLOUT_NOTE_BORDER,
    CALLOUT_TIP_BG,
    CALLOUT_TIP_BORDER,
    PAGE_MARGIN,
    PATTERN_TABLE_HEADERS,
    STYLE_BODY_TEXT,
    STYLE_CALLOUT_BODY,
    STYLE_CHAPTER_TITLE,
    STYLE_COVER_META,
    STYLE_SECTION_HEADING,
    STYLE_TOC_HEADING,
    STYLE_TOC_LEVEL0,
    STYLE_TOC_LEVEL1,
    TOC_HEADING,
    build_manual_styles,
    mono_span,
)
from src.export.pdf_colors import PRIMARY
from src.export.pdf_fonts import pdf_font_name

_COVER_BAND_HEIGHT = 2.5 * inch
_FONT_NAME = pdf_font_name()
_OUTLINE_KEY_PREFIX = "manual-"


def _attach_outline_hooks(doc: SimpleDocTemplate) -> None:
    def after_flowable(flowable: Flowable) -> None:
        if not isinstance(flowable, Paragraph):
            return

        style_name = flowable.style.name
        plain_text = flowable.getPlainText()
        if style_name == STYLE_CHAPTER_TITLE:
            key = f"{_OUTLINE_KEY_PREFIX}ch-{plain_text}"
            doc.canv.bookmarkPage(key)
            doc.canv.addOutlineEntry(plain_text, key, level=0, closed=False)
            doc.notify("TOCEntry", (0, plain_text, doc.page))
        elif style_name == STYLE_SECTION_HEADING:
            key = f"{_OUTLINE_KEY_PREFIX}sec-{plain_text}"
            doc.canv.bookmarkPage(key)
            doc.canv.addOutlineEntry(plain_text, key, level=1, closed=False)
            doc.notify("TOCEntry", (1, plain_text, doc.page))

    doc.afterFlowable = after_flowable


def _paragraph_body_html(text: str) -> str:
    return text.replace("\n\n", "<br/><br/>")


def _truncate_footer_title(title: str, *, max_len: int = 48) -> str:
    if len(title) <= max_len:
        return title
    return f"{title[: max_len - 1]}…"


def _cover_metadata_lines() -> tuple[str, str]:
    generated = datetime.now(UTC).strftime("%Y-%m-%d")
    return (
        f"Manual version: {MANUAL_VERSION}",
        f"Generated: {generated}",
    )


def _draw_cover_band(canvas: object, doc: object) -> None:
    width, height = letter
    canv = canvas
    canv.saveState()  # type: ignore[attr-defined]
    canv.setFillColor(PRIMARY)  # type: ignore[attr-defined]
    canv.rect(0, height - _COVER_BAND_HEIGHT, width, _COVER_BAND_HEIGHT, fill=1, stroke=0)  # type: ignore[attr-defined]
    canv.setFillColor(colors.white)  # type: ignore[attr-defined]
    canv.setFont(_FONT_NAME, 26)  # type: ignore[attr-defined]
    canv.drawCentredString(width / 2, height - inch, manual_title())  # type: ignore[attr-defined]
    canv.setFont(_FONT_NAME, 16)  # type: ignore[attr-defined]
    canv.drawCentredString(width / 2, height - 1.45 * inch, manual_subtitle())  # type: ignore[attr-defined]
    canv.restoreState()  # type: ignore[attr-defined]


def _draw_page_footer(canvas: object, doc: object, footer_title: str) -> None:
    width, _height = letter
    canv = canvas
    canv.saveState()  # type: ignore[attr-defined]
    canv.setFont(_FONT_NAME, 9)  # type: ignore[attr-defined]
    canv.setFillColor(colors.HexColor("#64748B"))  # type: ignore[attr-defined]
    page_num = getattr(doc, "page", 1)
    canv.drawRightString(width - PAGE_MARGIN, PAGE_MARGIN / 2, f"Page {page_num}")  # type: ignore[attr-defined]
    canv.drawString(PAGE_MARGIN, PAGE_MARGIN / 2, _truncate_footer_title(footer_title))  # type: ignore[attr-defined]
    canv.restoreState()  # type: ignore[attr-defined]


def _on_first_page(canvas: object, doc: object) -> None:
    _draw_cover_band(canvas, doc)


def _make_on_later_pages(footer_title: str) -> Callable[[object, object], None]:
    def _on_later_pages(canvas: object, doc: object) -> None:
        _draw_page_footer(canvas, doc, footer_title)

    return _on_later_pages


def _callout_label(block_type: ManualBlockType) -> str:
    if block_type is ManualBlockType.TIP:
        return CALLOUT_LABEL_TIP
    if block_type is ManualBlockType.NOTE:
        return CALLOUT_LABEL_NOTE
    return CALLOUT_LABEL_IMPORTANT


def _callout_colors(block_type: ManualBlockType) -> tuple[object, object]:
    if block_type is ManualBlockType.TIP:
        return CALLOUT_TIP_BORDER, CALLOUT_TIP_BG
    if block_type is ManualBlockType.NOTE:
        return CALLOUT_NOTE_BORDER, CALLOUT_NOTE_BG
    return CALLOUT_IMPORTANT_BORDER, CALLOUT_IMPORTANT_BG


def _callout_flowable(
    block: ManualBlock,
    styles: dict[str, ParagraphStyle],
    content_width: float,
) -> Table:
    label = block.title or _callout_label(block.block_type)
    body_html = _paragraph_body_html(block.text)
    paragraph = Paragraph(
        f"<b>{label}</b> {body_html}",
        styles[STYLE_CALLOUT_BODY],
    )
    border_color, background = _callout_colors(block.block_type)
    table = Table([[paragraph]], colWidths=[content_width])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), background),
                ("LEFTPADDING", (0, 0), (-1, -1), 12),
                ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("LINEBEFORE", (0, 0), (0, -1), 4, border_color),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    return table


def _bullet_list_flowable(
    block: ManualBlock,
    styles: dict[str, ParagraphStyle],
) -> list[Flowable]:
    items = [line for line in block.text.split("\n") if line.strip()]
    flowables: list[Flowable] = []
    for item in items:
        flowables.append(Paragraph(f"• {item}", styles[STYLE_BODY_TEXT]))
    return flowables


def _pattern_table_flowable(
    block: ManualBlock,
    styles: dict[str, ParagraphStyle],
    content_width: float,
) -> Table:
    rows: list[list[str]] = [list(PATTERN_TABLE_HEADERS)]
    for line in block.text.split("\n"):
        if not line.strip():
            continue
        pattern, _, meaning = line.partition("\t")
        rows.append(
            [
                Paragraph(mono_span(pattern), styles[STYLE_BODY_TEXT]),
                Paragraph(meaning, styles[STYLE_BODY_TEXT]),
            ]
        )
    col_width = content_width / 2
    table = Table(rows, colWidths=[col_width, col_width], repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
                ("FONTNAME", (0, 0), (-1, 0), _FONT_NAME),
                ("FONTSIZE", (0, 0), (-1, 0), 10),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#0F172A")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    if block.title:
        caption = Paragraph(f"<b>{block.title}</b>", styles[STYLE_BODY_TEXT])
        wrapper = Table([[caption], [table]], colWidths=[content_width])
        wrapper.setStyle(TableStyle([("BOTTOMPADDING", (0, 0), (0, 0), 4)]))
        return wrapper
    return table


def _block_flowables(
    block: ManualBlock,
    styles: dict[str, ParagraphStyle],
    content_width: float,
) -> list[Flowable]:
    if block.block_type is ManualBlockType.PARAGRAPH:
        return [
            Paragraph(_paragraph_body_html(block.text), styles[STYLE_BODY_TEXT]),
        ]
    if block.block_type is ManualBlockType.BULLET_LIST:
        return _bullet_list_flowable(block, styles)
    if block.block_type in {
        ManualBlockType.TIP,
        ManualBlockType.NOTE,
        ManualBlockType.IMPORTANT,
    }:
        return [_callout_flowable(block, styles, content_width)]
    if block.block_type is ManualBlockType.PATTERN_TABLE:
        return [_pattern_table_flowable(block, styles, content_width)]
    return []


def _build_table_of_contents(styles: dict[str, ParagraphStyle]) -> TableOfContents:
    toc = TableOfContents()
    toc.levelStyles = [
        styles[STYLE_TOC_LEVEL0],
        styles[STYLE_TOC_LEVEL1],
    ]
    toc.dotsMinLevel = 0
    return toc


def build_manual_story(
    chapters: Sequence[ManualChapter],
    *,
    content_width: float | None = None,
) -> list[Flowable]:
    """Build Platypus flowables for the user manual (testable without writing a file)."""
    styles = build_manual_styles()
    width = content_width if content_width is not None else letter[0] - 2 * PAGE_MARGIN
    version_line, generated_line = _cover_metadata_lines()

    story: list[Flowable] = [
        Spacer(1, _COVER_BAND_HEIGHT),
        Paragraph(version_line, styles[STYLE_COVER_META]),
        Paragraph(generated_line, styles[STYLE_COVER_META]),
        PageBreak(),
        Paragraph(TOC_HEADING, styles[STYLE_TOC_HEADING]),
        Spacer(1, 0.15 * inch),
        _build_table_of_contents(styles),
        PageBreak(),
    ]

    for index, chapter in enumerate(chapters):
        if index > 0:
            story.append(PageBreak())
        story.append(Paragraph(chapter.title, styles[STYLE_CHAPTER_TITLE]))
        for section in chapter.sections:
            story.append(Paragraph(section.heading, styles[STYLE_SECTION_HEADING]))
            story.append(
                HRFlowable(
                    width="100%",
                    thickness=0.5,
                    color=colors.HexColor("#E2E8F0"),
                    spaceBefore=2,
                    spaceAfter=8,
                )
            )
            for block in section.blocks:
                story.extend(_block_flowables(block, styles, width))
            story.append(Spacer(1, 0.1 * inch))

    return story


def pdf_page_count(path: Path) -> int:
    """Return the number of pages in a PDF file."""
    data = path.read_bytes()
    return len(re.findall(rb"/Type\s*/Page(?!s)", data))


def pdf_contains_text(path: Path, text: str) -> bool:
    """Return whether plain text appears in a PDF (best-effort, no extra dependencies)."""
    data = path.read_bytes()
    if text.encode() in data:
        return True
    return text.encode("utf-16-be") in data


def pdf_has_chapter_outlines(path: Path, chapter_titles: Sequence[str]) -> bool:
    """Return whether all chapter titles appear in PDF outline metadata."""
    data = path.read_bytes().decode("latin-1", errors="ignore")
    return all(title in data for title in chapter_titles)


class ManualPdfExporter:
    def export(
        self,
        output_path: Path,
        *,
        locale: str | None = None,
        chapters: Sequence[ManualChapter] | None = None,
    ) -> None:
        """Write the user manual PDF.

        ``locale`` is reserved for callers that install a ``QTranslator`` before
        invoking export (see ``scripts/generate_manual.py`` in Task 29_4).
        """
        del locale
        manual = tuple(chapters) if chapters is not None else manual_chapters()
        footer_title = f"{manual_title()} — {manual_subtitle()}"

        def _write(target: Path) -> None:
            doc = SimpleDocTemplate(
                str(target),
                pagesize=letter,
                leftMargin=PAGE_MARGIN,
                rightMargin=PAGE_MARGIN,
                topMargin=PAGE_MARGIN,
                bottomMargin=PAGE_MARGIN,
                onFirstPage=_on_first_page,
                onLaterPages=_make_on_later_pages(footer_title),
            )
            _attach_outline_hooks(doc)
            story = build_manual_story(manual, content_width=doc.width)
            try:
                doc.multiBuild(story)
            except OSError as exc:
                raise ExportError(str(exc)) from exc

        atomic_write(output_path, _write)
