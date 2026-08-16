from __future__ import annotations

import shutil
import uuid
from pathlib import Path

from src.app.identity import RECEIPTS_DIRECTORY_NAME
from src.domain.exceptions import ReceiptImageError, ReceiptImagePathError

_ALLOWED_SUFFIXES = frozenset({".jpg", ".jpeg", ".png", ".webp", ".heic"})


def normalize_receipt_relative_path(relative_path: str) -> str:
    """Return a safe receipt path relative to the app data root."""
    cleaned = relative_path.strip().replace("\\", "/")
    if not cleaned:
        msg = "Receipt image path is required"
        raise ReceiptImagePathError(msg)
    if cleaned.startswith("/") or cleaned.startswith("../") or "/../" in cleaned:
        msg = "Receipt image path must stay under app data"
        raise ReceiptImagePathError(msg)
    parts = [part for part in cleaned.split("/") if part not in {"", "."}]
    if not parts or ".." in parts:
        msg = "Receipt image path must stay under app data"
        raise ReceiptImagePathError(msg)
    normalized = "/".join(parts)
    if not normalized.startswith(f"{RECEIPTS_DIRECTORY_NAME}/"):
        msg = f"Receipt image path must start with {RECEIPTS_DIRECTORY_NAME}/"
        raise ReceiptImagePathError(msg)
    return normalized


class ReceiptImageStore:
    """Stores receipt image files under the application data directory."""

    def __init__(self, app_data_dir: Path) -> None:
        self._app_data_dir = app_data_dir.resolve()

    @property
    def app_data_dir(self) -> Path:
        return self._app_data_dir

    def receipts_root(self) -> Path:
        root = self._app_data_dir / RECEIPTS_DIRECTORY_NAME
        root.mkdir(parents=True, exist_ok=True)
        return root

    def resolve_path(self, relative_path: str) -> Path:
        normalized = normalize_receipt_relative_path(relative_path)
        resolved = (self._app_data_dir / normalized).resolve()
        if not resolved.is_relative_to(self._app_data_dir):
            msg = "Receipt image path must stay under app data"
            raise ReceiptImagePathError(msg)
        return resolved

    def save_receipt_image(self, expense_id: str, source_image: Path) -> str:
        if not expense_id.strip():
            msg = "Expense id is required to store a receipt image"
            raise ReceiptImageError(msg)
        if not source_image.is_file():
            msg = f"Receipt image not found: {source_image}"
            raise ReceiptImageError(msg)

        suffix = source_image.suffix.lower()
        if suffix not in _ALLOWED_SUFFIXES:
            suffix = ".jpg"

        destination_dir = self.receipts_root() / expense_id
        destination_dir.mkdir(parents=True, exist_ok=True)
        filename = f"{uuid.uuid4()}{suffix}"
        destination = destination_dir / filename
        shutil.copy2(source_image, destination)
        return f"{RECEIPTS_DIRECTORY_NAME}/{expense_id}/{filename}"

    def delete_receipt_image(self, relative_path: str | None) -> None:
        if relative_path is None or relative_path.strip() == "":
            return
        image_path = self.resolve_path(relative_path)
        if image_path.is_file():
            image_path.unlink()
        expense_dir = image_path.parent
        if expense_dir.is_dir() and expense_dir != self.receipts_root():
            try:
                expense_dir.rmdir()
            except OSError:
                pass
