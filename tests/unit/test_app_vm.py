from __future__ import annotations

import pytest
from PySide6.QtCore import QObject

from src.app.viewmodels.app_vm import AppViewModel
from src.domain.currencies import COMMON_CURRENCIES


@pytest.mark.unit
def test_app_view_model_exposes_common_currencies(qt_app: QObject) -> None:
    _ = qt_app
    vm = AppViewModel()

    assert vm.commonCurrencies == list(COMMON_CURRENCIES)
