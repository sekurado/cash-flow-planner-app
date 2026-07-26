from __future__ import annotations

from functools import lru_cache
from pathlib import Path

_FALLBACK_FONT = "Helvetica"
_FONT_FILE_NAME = "DejaVuSans.ttf"
_REGISTERED_FONT_NAME = "DejaVuSans"


@lru_cache(maxsize=1)
def pdf_font_name() -> str:
    """Return a ReportLab font with Unicode coverage, falling back to Helvetica."""
    try:
        _ensure_font_registered()
    except OSError:
        return _FALLBACK_FONT
    return _REGISTERED_FONT_NAME


def _font_file_path() -> Path:
    return Path(__file__).resolve().parent / "fonts" / _FONT_FILE_NAME


def _ensure_font_registered() -> None:
    from reportlab.pdfbase import pdfmetrics  # type: ignore[import-untyped]
    from reportlab.pdfbase.ttfonts import TTFont  # type: ignore[import-untyped]

    if _REGISTERED_FONT_NAME in pdfmetrics.getRegisteredFontNames():
        return

    font_path = _font_file_path()
    if not font_path.is_file():
        msg = f"PDF Unicode font not found: {font_path}"
        raise OSError(msg)

    pdfmetrics.registerFont(TTFont(_REGISTERED_FONT_NAME, str(font_path)))
