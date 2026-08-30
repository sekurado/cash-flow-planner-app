from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import QObject, QRunnable, Signal


class ReceiptOcrInstallWorkerSignals(QObject):
    finished = Signal()
    error = Signal(str)


class ReceiptOcrInstallWorker(QRunnable):
    """Install on-device OCR bindings off the UI thread."""

    def __init__(self, installer: Callable[[], None]) -> None:
        super().__init__()
        self._installer = installer
        self.signals = ReceiptOcrInstallWorkerSignals()

    def run(self) -> None:
        try:
            self._installer()
        except Exception as exc:
            self.signals.error.emit(str(exc))
            return
        self.signals.finished.emit()
