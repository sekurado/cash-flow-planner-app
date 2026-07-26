from __future__ import annotations

import pytest
from sqlalchemy import Engine, inspect


@pytest.mark.integration
def test_in_memory_engine_has_all_tables(in_memory_engine: Engine) -> None:
    table_names = set(inspect(in_memory_engine).get_table_names())
    expected = {"plans", "entries", "exchange_rates", "simulation_runs"}
    assert expected.issubset(table_names)


@pytest.mark.integration
def test_qt_app_is_singleton(qt_app: object) -> None:
    from PySide6.QtWidgets import QApplication

    assert QApplication.instance() is qt_app
