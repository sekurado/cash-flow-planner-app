from __future__ import annotations

import os
from collections.abc import Generator
from dataclasses import dataclass
from pathlib import Path

import pytest
from PySide6.QtCore import QUrl
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtWidgets import QApplication
from sqlalchemy.engine import Connection, Engine

from main import bootstrap_view_models
from src.app.viewmodels.app_vm import AppViewModel
from src.app.viewmodels.audit_log_vm import AuditLogViewModel
from src.app.viewmodels.currency_vm import CurrencyViewModel
from src.app.viewmodels.entries_vm import EntriesViewModel
from src.app.viewmodels.plan_import_vm import PlanImportViewModel
from src.app.viewmodels.plan_vm import PlanViewModel
from src.app.viewmodels.recorded_expenses_view_model import RecordedExpensesViewModel
from src.app.viewmodels.settings_vm import SettingsViewModel
from src.app.viewmodels.simulation_vm import SimulationViewModel
from src.app.viewmodels.suggestions_vm import SuggestionsViewModel
from src.data.database import create_engine_for_path, resolve_database_path
from src.data.migrate import run_migrations

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

ROOT_DIR = Path(__file__).resolve().parents[2]
QML_MAIN = ROOT_DIR / "qml" / "main.qml"


@pytest.fixture(scope="session")
def qgui_app(qt_app: QApplication) -> QApplication:
    """Reuse session QApplication for QML E2E tests."""
    return qt_app


@pytest.fixture
def qml_engine(
    tmp_path: Path, qgui_app: QApplication
) -> Generator[QQmlApplicationEngine, None, None]:
    """QQmlApplicationEngine backed by a migrated temp-file database."""
    _ = qgui_app
    db_path = resolve_database_path(data_dir=tmp_path)
    run_migrations(db_path=db_path)

    QQuickStyle.setStyle("Material")
    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("appViewModel", AppViewModel())
    engine.rootContext().setContextProperty("settingsViewModel", SettingsViewModel())
    engine.load(QUrl.fromLocalFile(str(QML_MAIN)))

    if not engine.rootObjects():
        msg = f"Failed to load QML entry point: {QML_MAIN}"
        raise RuntimeError(msg)

    yield engine

    engine.deleteLater()


@pytest.fixture
def e2e_db_engine(tmp_path: Path) -> Generator[object, None, None]:
    """SQLAlchemy engine for the E2E temp database after migrations."""
    db_path = resolve_database_path(data_dir=tmp_path)
    run_migrations(db_path=db_path)
    engine = create_engine_for_path(db_path)
    yield engine
    engine.dispose()


@dataclass
class E2EStack:
    """ViewModels backed by a temp-file database, matching the production bootstrap."""

    plan_vm: PlanViewModel
    entries_vm: EntriesViewModel
    simulation_vm: SimulationViewModel
    suggestions_vm: SuggestionsViewModel
    currency_vm: CurrencyViewModel
    plan_import_vm: PlanImportViewModel
    audit_log_vm: AuditLogViewModel
    recorded_expenses_vm: RecordedExpensesViewModel


@pytest.fixture
def e2e_stack(tmp_path: Path, qt_app: object) -> Generator[E2EStack, None, None]:
    """Full application stack wired to a migrated temp-file database."""
    _ = qt_app
    db_path = resolve_database_path(data_dir=tmp_path)
    run_migrations(db_path=db_path)
    (
        plan_vm,
        entries_vm,
        simulation_vm,
        suggestions_vm,
        _,
        plan_import_vm,
        currency_vm,
        audit_log_vm,
        recorded_expenses_vm,
        db_engine,
        db_conn,
    ) = bootstrap_view_models(db_path)
    stack = E2EStack(
        plan_vm=plan_vm,
        entries_vm=entries_vm,
        simulation_vm=simulation_vm,
        suggestions_vm=suggestions_vm,
        currency_vm=currency_vm,
        plan_import_vm=plan_import_vm,
        audit_log_vm=audit_log_vm,
        recorded_expenses_vm=recorded_expenses_vm,
    )
    yield stack
    _dispose_db(db_conn, db_engine)


def _dispose_db(db_conn: Connection, db_engine: Engine) -> None:
    db_conn.close()
    db_engine.dispose()
