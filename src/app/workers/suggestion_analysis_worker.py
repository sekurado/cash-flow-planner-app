from __future__ import annotations

from collections.abc import Sequence

from PySide6.QtCore import QObject, QRunnable, Signal

from src.domain.entities import Entry, SimulationResult
from src.domain.suggestions import SuggestionEngine


class SuggestionAnalysisWorkerSignals(QObject):
    finished = Signal(list)
    error = Signal(str)


class SuggestionAnalysisWorker(QRunnable):
    def __init__(
        self,
        engine: SuggestionEngine,
        entries: Sequence[Entry],
        result: SimulationResult,
    ) -> None:
        super().__init__()
        self._engine = engine
        self._entries = list(entries)
        self._result = result
        self.signals = SuggestionAnalysisWorkerSignals()

    def run(self) -> None:
        try:
            suggestions = list(self._engine.analyze(self._entries, self._result))
            self.signals.finished.emit(suggestions)
        except Exception as exc:
            self.signals.error.emit(str(exc))
