from __future__ import annotations

from pathlib import Path

import pytest

from src.app.identity import RECEIPTS_DIRECTORY_NAME
from src.domain.exceptions import ReceiptImagePathError
from src.domain.receipt_image_store import ReceiptImageStore, normalize_receipt_relative_path


@pytest.mark.unit
def test_normalize_receipt_relative_path_accepts_receipts_subpath() -> None:
    assert (
        normalize_receipt_relative_path("receipts/expense-1/receipt.jpg")
        == "receipts/expense-1/receipt.jpg"
    )


@pytest.mark.unit
@pytest.mark.parametrize(
    "relative_path",
    [
        "../secrets.txt",
        "/etc/passwd",
        "receipts/../outside.jpg",
        "other/file.jpg",
    ],
)
def test_normalize_receipt_relative_path_rejects_escape(relative_path: str) -> None:
    with pytest.raises(ReceiptImagePathError):
        normalize_receipt_relative_path(relative_path)


@pytest.mark.unit
def test_save_and_resolve_receipt_image_stays_under_app_data(tmp_path: Path) -> None:
    app_data = tmp_path / "appdata"
    app_data.mkdir()
    store = ReceiptImageStore(app_data)
    source = tmp_path / "camera.jpg"
    source.write_bytes(b"fake-jpeg")

    relative = store.save_receipt_image("expense-123", source)
    resolved = store.resolve_path(relative)

    assert relative == f"{RECEIPTS_DIRECTORY_NAME}/expense-123/{resolved.name}"
    assert resolved.is_file()
    assert resolved.is_relative_to(app_data.resolve())


@pytest.mark.unit
def test_delete_receipt_image_removes_file(tmp_path: Path) -> None:
    app_data = tmp_path / "appdata"
    store = ReceiptImageStore(app_data)
    source = tmp_path / "camera.png"
    source.write_bytes(b"fake-png")

    relative = store.save_receipt_image("expense-456", source)
    resolved = store.resolve_path(relative)
    assert resolved.is_file()

    store.delete_receipt_image(relative)

    assert not resolved.exists()
