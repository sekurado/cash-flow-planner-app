from __future__ import annotations

from collections.abc import Sequence
from datetime import date
from pathlib import Path

import pytest
from PySide6.QtCore import QThreadPool

from src.app.workers.receipt_ocr_worker import ReceiptOcrWorker
from src.domain.receipt_field_parser import ReceiptFieldParser
from src.integrations.receipt_ocr.macos_vision import MacosVisionOcrProvider
from src.integrations.receipt_ocr.unsupported import UnsupportedReceiptOcrProvider


@pytest.mark.integration
def test_worker_emits_parsed_fields(qtbot: object, tmp_path: Path) -> None:
    image = tmp_path / "receipt.jpg"
    image.write_bytes(b"fake-bytes")

    def recognize(path: Path) -> Sequence[tuple[str, float]]:
        _ = path
        return (("Cafe Nero", 1.0), ("Date: 2026-01-15", 1.0), ("TOTAL 12.50", 1.0))

    worker = ReceiptOcrWorker(
        MacosVisionOcrProvider(recognize=recognize),
        ReceiptFieldParser(reference_date=date(2026, 8, 29)),
        image,
    )

    with qtbot.waitSignal(worker.signals.finished, timeout=5000) as blocker:  # type: ignore[attr-defined]
        QThreadPool.globalInstance().start(worker)

    payload = blocker.args[0]
    assert payload["ocr"]["provider_id"] == "vision-macos"
    assert payload["fields"]["amount"] == pytest.approx(12.50)
    assert payload["fields"]["occurred_on"] == "2026-01-15"
    assert payload["fields"]["merchant"] == "Cafe Nero"


@pytest.mark.integration
def test_worker_emits_error_when_ocr_unavailable(qtbot: object, tmp_path: Path) -> None:
    image = tmp_path / "receipt.jpg"
    image.write_bytes(b"fake-bytes")
    worker = ReceiptOcrWorker(
        UnsupportedReceiptOcrProvider(platform="linux"),
        ReceiptFieldParser(reference_date=date(2026, 8, 29)),
        image,
    )

    with qtbot.waitSignal(worker.signals.error, timeout=5000) as blocker:  # type: ignore[attr-defined]
        QThreadPool.globalInstance().start(worker)

    message = blocker.args[0]
    assert "linux" in message
