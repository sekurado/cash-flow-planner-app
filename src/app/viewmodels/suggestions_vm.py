from __future__ import annotations

from typing import Any

from PySide6.QtCore import Property, QObject, QThreadPool, Signal, Slot

from src.app.i18n.suggestion_copy import localize_suggestions
from src.app.models.suggestion_list_model import (
    SuggestionListModel,
    _impact_formatted,
    _suggested_change_json,
)
from src.app.viewmodels.error_support import ErrorSupport
from src.app.workers.simulation_worker import deserialize_simulation_result
from src.app.workers.suggestion_analysis_worker import SuggestionAnalysisWorker
from src.data.repositories.entry_repo import AbstractEntryRepository
from src.domain.entities import Entry
from src.domain.suggestion_deficit import DEFICIT_ANALYZER_FUNCS
from src.domain.suggestion_surplus import SURPLUS_ANALYZER_FUNCS
from src.domain.suggestions import Suggestion, SuggestionEngine


def _default_engine() -> SuggestionEngine:
    return SuggestionEngine(analyzers=[*DEFICIT_ANALYZER_FUNCS, *SURPLUS_ANALYZER_FUNCS])


def _suggestion_to_dict(suggestion: Suggestion) -> dict[str, Any]:
    return {
        "suggestionId": suggestion.id,
        "kind": suggestion.kind.value,
        "title": suggestion.title,
        "detail": suggestion.detail,
        "impactAmount": suggestion.impact_amount,
        "impactCurrency": suggestion.impact_currency,
        "impactFormatted": _impact_formatted(suggestion),
        "relatedEntryId": suggestion.related_entry_id or "",
        "hasSuggestedChange": suggestion.suggested_change is not None,
        "suggestedChangeJson": _suggested_change_json(suggestion.suggested_change),
    }


class SuggestionsViewModel(QObject):
    """Exposes cash-flow suggestions to QML after baseline simulation completes."""

    hasSuggestionsChanged = Signal()
    isAnalyzingChanged = Signal()
    errorChanged = Signal()

    def __init__(
        self,
        entry_repo: AbstractEntryRepository,
        *,
        engine: SuggestionEngine | None = None,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._entry_repo = entry_repo
        self._engine = engine or _default_engine()
        self._list_model = SuggestionListModel(parent=self)
        self._is_analyzing = False
        self._errors = ErrorSupport(self)
        self._worker: SuggestionAnalysisWorker | None = None
        self._raw_suggestions: list[Suggestion] = []
        self._list_model.countChanged.connect(self._on_count_changed)

    @Property(QObject, constant=True)
    def suggestions(self) -> SuggestionListModel:
        return self._list_model

    @Property(bool, notify=hasSuggestionsChanged)
    def hasSuggestions(self) -> bool:
        return self._list_model.item_count() > 0

    @Property(bool, notify=isAnalyzingChanged)
    def isAnalyzing(self) -> bool:
        return self._is_analyzing

    @Property(str, notify=errorChanged)
    def error(self) -> str:
        return self._errors.message

    @Slot(str, "QVariant")
    def refreshForPlan(self, plan_id: str, result: object) -> None:
        try:
            self._clear_error()
            if not isinstance(result, dict):
                msg = "Simulation result must be a mapping"
                raise TypeError(msg)
            entries = [
                entry for entry in self._entry_repo.find_by_plan_id(plan_id) if entry.is_active
            ]
            simulation_result = deserialize_simulation_result(result)
            self._start_analysis(entries, simulation_result)
        except Exception as exc:
            self._set_error(exc)

    @Slot("QVariant", "QVariant")
    def refresh(self, entries: object, result: object) -> None:
        try:
            self._clear_error()
            if not isinstance(entries, list):
                msg = "Entries must be a list"
                raise TypeError(msg)
            if not isinstance(result, dict):
                msg = "Simulation result must be a mapping"
                raise TypeError(msg)
            active_entries = [
                entry for entry in entries if isinstance(entry, Entry) and entry.is_active
            ]
            simulation_result = deserialize_simulation_result(result)
            self._start_analysis(active_entries, simulation_result)
        except Exception as exc:
            self._set_error(exc)

    @Slot()
    def clear(self) -> None:
        self._worker = None
        if self._is_analyzing:
            self._is_analyzing = False
            self.isAnalyzingChanged.emit()
        self._list_model.reset([])
        self._raw_suggestions = []
        self._clear_error()

    @Slot()
    def clearError(self) -> None:
        self._clear_error()

    @Slot(int, result="QVariant")
    def suggestionAt(self, index: int) -> dict[str, Any] | None:
        suggestion = self._list_model.suggestion_at(index)
        if suggestion is None:
            return None
        return _suggestion_to_dict(suggestion)

    @Slot()
    def retranslate(self) -> None:
        self._errors.retranslate()
        if not self._raw_suggestions:
            return
        self._list_model.reset(localize_suggestions(self._raw_suggestions))

    def _start_analysis(self, entries: list[Entry], result: object) -> None:
        from src.domain.entities import SimulationResult

        if not isinstance(result, SimulationResult):
            msg = "Simulation result is required for suggestion analysis"
            raise TypeError(msg)

        self._is_analyzing = True
        self.isAnalyzingChanged.emit()

        worker = SuggestionAnalysisWorker(self._engine, entries, result)
        worker.signals.finished.connect(self._on_analysis_finished)
        worker.signals.error.connect(self._on_analysis_error)
        self._worker = worker
        QThreadPool.globalInstance().start(worker)

    def _on_analysis_finished(self, suggestions: list[Suggestion]) -> None:
        self._worker = None
        self._is_analyzing = False
        self._raw_suggestions = list(suggestions)
        self._list_model.reset(localize_suggestions(self._raw_suggestions))
        self.isAnalyzingChanged.emit()

    def _on_analysis_error(self, message: str) -> None:
        self._worker = None
        self._is_analyzing = False
        self._raw_suggestions = []
        self._list_model.reset([])
        self.isAnalyzingChanged.emit()
        self._set_error(message)

    def _on_count_changed(self) -> None:
        self.hasSuggestionsChanged.emit()

    def _set_error(self, exc: BaseException | str) -> None:
        if isinstance(exc, BaseException):
            self._errors.set_from_exception(exc)
            return
        self._errors.set(exc)

    def _clear_error(self) -> None:
        if not self._errors.clear():
            return
        self.errorChanged.emit()
