from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QObject, QRunnable, Signal

from src.domain.receipt_field_parser import ReceiptFieldHints, ReceiptFieldParser
from src.domain.receipt_ocr import ReceiptOcrProvider, ReceiptOcrResult


class ReceiptOcrWorkerSignals(QObject):
    finished = Signal(dict)
    error = Signal(str)


class ReceiptOcrWorker(QRunnable):
    """Run OCR + field parsing off the UI thread."""

    def __init__(
        self,
        provider: ReceiptOcrProvider,
        parser: ReceiptFieldParser,
        image_path: Path,
    ) -> None:
        super().__init__()
        self._provider = provider
        self._parser = parser
        self._image_path = image_path
        self.signals = ReceiptOcrWorkerSignals()

    def run(self) -> None:
        try:
            ocr_result = self._provider.extract_text(self._image_path)
            hints = self._parser.parse(ocr_result)
            self.signals.finished.emit(_payload(ocr_result, hints))
        except Exception as exc:
            self.signals.error.emit(str(exc))


def _payload(ocr_result: ReceiptOcrResult, hints: ReceiptFieldHints) -> dict[str, object]:
    return {
        "ocr": ocr_result.model_dump(mode="json"),
        "fields": hints.model_dump(mode="json"),
    }
