from __future__ import annotations

from PySide6.QtCore import Property, QObject, Signal

from src.domain.currencies import COMMON_CURRENCIES


class AppViewModel(QObject):
    """Application-level state exposed to the root QML shell."""

    appNameChanged = Signal()

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._app_name = "Cash Flow Planner"

    @Property(str, notify=appNameChanged)
    def appName(self) -> str:
        return self._app_name

    @Property("QVariantList", constant=True)  # type: ignore[arg-type]
    def commonCurrencies(self) -> list[str]:
        return list(COMMON_CURRENCIES)
