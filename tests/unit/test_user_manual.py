from __future__ import annotations

from unittest.mock import patch

import pytest
from PySide6.QtWidgets import QApplication

from src.app.user_manual import (
    manual_qrc_path,
    materialize_manual_pdf,
    open_user_manual,
    resolve_manual_qrc_path,
)


@pytest.mark.unit
def test_manual_qrc_path_uses_locale_suffix() -> None:
    assert manual_qrc_path("en") == ":/manual/CashFlowPlanner-UserManual_en.pdf"


@pytest.mark.unit
def test_resolve_manual_qrc_path_falls_back_to_english(qt_app: QApplication) -> None:
    del qt_app
    with patch("src.app.user_manual.QFile.exists") as exists:
        exists.side_effect = lambda path: path == manual_qrc_path("en")
        assert resolve_manual_qrc_path("fr") == manual_qrc_path("en")


@pytest.mark.unit
def test_resolve_manual_qrc_path_prefers_requested_locale(qt_app: QApplication) -> None:
    del qt_app
    import src.app.resources_rc  # noqa: F401

    assert resolve_manual_qrc_path("fr") == manual_qrc_path("fr")
    assert resolve_manual_qrc_path("de") == manual_qrc_path("de")


@pytest.mark.unit
def test_open_user_manual_raises_when_missing(qt_app: QApplication) -> None:
    del qt_app
    with patch("src.app.user_manual.resolve_manual_qrc_path", return_value=None):
        with pytest.raises(Exception, match="User manual is not available"):
            open_user_manual("en")


@pytest.mark.unit
def test_materialize_manual_pdf_writes_cache_copy(qt_app: QApplication) -> None:
    del qt_app
    import src.app.resources_rc  # noqa: F401

    qrc_path = resolve_manual_qrc_path("en")
    assert qrc_path is not None

    pdf_path = materialize_manual_pdf(qrc_path)

    assert pdf_path.is_file()
    assert pdf_path.name == "CashFlowPlanner-UserManual_en.pdf"
    assert pdf_path.read_bytes()[:4] == b"%PDF"
