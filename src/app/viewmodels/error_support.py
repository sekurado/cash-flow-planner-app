from __future__ import annotations

from PySide6.QtCore import QObject

from src.app.i18n.user_messages import format_view_model_error, translate_user_message


class ErrorSupport:
    """Shared translated error state for ViewModels."""

    def __init__(self, owner: QObject) -> None:
        self._owner = owner
        self._error_source = ""
        self._error = ""

    @property
    def message(self) -> str:
        return self._error

    def set(self, source: str) -> None:
        self._error_source = source
        self._error = translate_user_message(source)
        self._owner.errorChanged.emit()  # type: ignore[attr-defined]

    def set_from_exception(self, exc: BaseException) -> None:
        self._error_source = str(exc)
        self._error = format_view_model_error(exc)
        self._owner.errorChanged.emit()  # type: ignore[attr-defined]

    def clear(self) -> bool:
        if not self._error_source:
            return False
        self._error_source = ""
        self._error = ""
        return True

    def retranslate(self) -> None:
        if not self._error_source:
            return
        translated = translate_user_message(self._error_source)
        if translated == self._error:
            return
        self._error = translated
        self._owner.errorChanged.emit()  # type: ignore[attr-defined]
