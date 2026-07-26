from __future__ import annotations

import json

from PySide6.QtCore import (
    Property,
    QAbstractListModel,
    QByteArray,
    QModelIndex,
    QObject,
    Qt,
    Signal,
)

from src.domain.suggestion_messages import format_currency_amount
from src.domain.suggestions import SuggestedChange, Suggestion


def _suggested_change_json(change: SuggestedChange | None) -> str:
    if change is None:
        return ""
    payload: dict[str, float] = {}
    if change.amount_delta is not None:
        payload["amount_delta"] = change.amount_delta
    if change.percent_delta is not None:
        payload["percent_delta"] = change.percent_delta
    if change.target_initial_balance is not None:
        payload["target_initial_balance"] = change.target_initial_balance
    return json.dumps(payload)


def _impact_formatted(suggestion: Suggestion) -> str:
    if suggestion.impact_amount is None:
        return ""
    return format_currency_amount(suggestion.impact_amount, suggestion.impact_currency)


class SuggestionListModel(QAbstractListModel):
    SUGGESTION_ID_ROLE = Qt.ItemDataRole.UserRole + 1
    KIND_ROLE = Qt.ItemDataRole.UserRole + 2
    TITLE_ROLE = Qt.ItemDataRole.UserRole + 3
    DETAIL_ROLE = Qt.ItemDataRole.UserRole + 4
    IMPACT_AMOUNT_ROLE = Qt.ItemDataRole.UserRole + 5
    IMPACT_CURRENCY_ROLE = Qt.ItemDataRole.UserRole + 6
    IMPACT_FORMATTED_ROLE = Qt.ItemDataRole.UserRole + 7
    RELATED_ENTRY_ID_ROLE = Qt.ItemDataRole.UserRole + 8
    HAS_SUGGESTED_CHANGE_ROLE = Qt.ItemDataRole.UserRole + 9
    SUGGESTED_CHANGE_JSON_ROLE = Qt.ItemDataRole.UserRole + 10

    countChanged = Signal()

    def __init__(
        self,
        suggestions: list[Suggestion] | None = None,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._suggestions: list[Suggestion] = list(suggestions) if suggestions is not None else []

    def item_count(self) -> int:
        return len(self._suggestions)

    @Property(int, notify=countChanged)
    def count(self) -> int:
        return len(self._suggestions)

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:  # type: ignore[override]  # noqa: N802
        if parent.isValid():
            return 0
        return len(self._suggestions)

    def data(  # type: ignore[override]  # noqa: N802
        self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole
    ) -> object | None:
        if not index.isValid():
            return None
        suggestion = self._suggestions[index.row()]
        match role:
            case self.SUGGESTION_ID_ROLE:
                return suggestion.id
            case self.KIND_ROLE:
                return suggestion.kind.value
            case self.TITLE_ROLE:
                return suggestion.title
            case self.DETAIL_ROLE:
                return suggestion.detail
            case self.IMPACT_AMOUNT_ROLE:
                return suggestion.impact_amount
            case self.IMPACT_CURRENCY_ROLE:
                return suggestion.impact_currency
            case self.IMPACT_FORMATTED_ROLE:
                return _impact_formatted(suggestion)
            case self.RELATED_ENTRY_ID_ROLE:
                return suggestion.related_entry_id or ""
            case self.HAS_SUGGESTED_CHANGE_ROLE:
                return suggestion.suggested_change is not None
            case self.SUGGESTED_CHANGE_JSON_ROLE:
                return _suggested_change_json(suggestion.suggested_change)
            case _:
                return None

    def roleNames(self) -> dict[int, QByteArray]:  # noqa: N802
        return {
            self.SUGGESTION_ID_ROLE: QByteArray(b"suggestionId"),
            self.KIND_ROLE: QByteArray(b"kind"),
            self.TITLE_ROLE: QByteArray(b"title"),
            self.DETAIL_ROLE: QByteArray(b"detail"),
            self.IMPACT_AMOUNT_ROLE: QByteArray(b"impactAmount"),
            self.IMPACT_CURRENCY_ROLE: QByteArray(b"impactCurrency"),
            self.IMPACT_FORMATTED_ROLE: QByteArray(b"impactFormatted"),
            self.RELATED_ENTRY_ID_ROLE: QByteArray(b"relatedEntryId"),
            self.HAS_SUGGESTED_CHANGE_ROLE: QByteArray(b"hasSuggestedChange"),
            self.SUGGESTED_CHANGE_JSON_ROLE: QByteArray(b"suggestedChangeJson"),
        }

    def reset(self, suggestions: list[Suggestion]) -> None:
        self.beginResetModel()
        self._suggestions = list(suggestions)
        self.endResetModel()
        self.countChanged.emit()

    def suggestion_at(self, index: int) -> Suggestion | None:
        if index < 0 or index >= len(self._suggestions):
            return None
        return self._suggestions[index]
