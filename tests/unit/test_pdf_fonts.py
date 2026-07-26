from __future__ import annotations

import pytest

from src.export.pdf_fonts import _font_file_path, pdf_font_name


@pytest.mark.unit
def test_pdf_font_file_is_bundled() -> None:
    font_path = _font_file_path()
    assert font_path.is_file()
    assert font_path.suffix == ".ttf"


@pytest.mark.unit
def test_pdf_font_name_registers_unicode_font() -> None:
    assert pdf_font_name() == "DejaVuSans"

    from reportlab.pdfbase import pdfmetrics  # type: ignore[import-untyped]

    assert "DejaVuSans" in pdfmetrics.getRegisteredFontNames()


@pytest.mark.unit
def test_pdf_font_name_falls_back_when_font_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    from src.export import pdf_fonts

    pdf_fonts.pdf_font_name.cache_clear()

    def _raise_missing() -> None:
        raise OSError("missing font")

    monkeypatch.setattr(pdf_fonts, "_ensure_font_registered", _raise_missing)

    assert pdf_font_name() == "Helvetica"

    pdf_fonts.pdf_font_name.cache_clear()
