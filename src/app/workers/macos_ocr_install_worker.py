from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import QObject, QRunnable, Signal


class MacosOcrInstallWorkerSignals(QObject):
    finished = Signal()
    error = Signal(str)


class MacosOcrInstallWorker(QRunnable):
    """Install macOS Vision OCR bindings off the UI thread."""

    def __init__(self, installer: Callable[[], None]) -> None:
        super().__init__()
        self._installer = installer
        self.signals = MacosOcrInstallWorkerSignals()

    def run(self) -> None:
        try:
            self._installer()
        except Exception as exc:
            self.signals.error.emit(str(exc))
            return
        self.signals.finished.emit()
