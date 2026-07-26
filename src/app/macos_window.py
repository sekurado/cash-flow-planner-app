from __future__ import annotations

import sys

from PySide6.QtCore import QTimer
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuick import QQuickWindow


def present_main_window(engine: QQmlApplicationEngine) -> None:
    """Bring the primary QML window to the foreground on macOS.

    Frozen macOS builds can finish loading QML while the dock icon is visible but the
    ``ApplicationWindow`` stays behind other apps or never receives activation from Launch
    Services (common with quarantined / first-launch installs).
    """
    if sys.platform != "darwin":
        return

    def activate() -> None:
        for root in engine.rootObjects():
            if not isinstance(root, QQuickWindow):
                continue
            root.setVisibility(QQuickWindow.Visibility.Windowed)
            root.show()
            root.raise_()
            root.requestActivate()

    # Defer once so Cocoa finishes registering the NSWindow.
    QTimer.singleShot(0, activate)
