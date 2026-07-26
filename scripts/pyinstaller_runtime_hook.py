"""PyInstaller runtime hook — runs before application code in frozen bundles."""

from __future__ import annotations

import os
import sys


def _clear_offscreen_platform() -> None:
    # CI / tests set QT_QPA_PLATFORM=offscreen; never ship that in a GUI bundle.
    if os.environ.get("QT_QPA_PLATFORM") == "offscreen":
        del os.environ["QT_QPA_PLATFORM"]


if getattr(sys, "frozen", False):
    _clear_offscreen_platform()
