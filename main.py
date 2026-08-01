from __future__ import annotations

import argparse
import logging
import os
import sys
import traceback
from logging.handlers import RotatingFileHandler
from pathlib import Path

import PySide6.QtCharts  # noqa: F401  # registers QtCharts QML module
from PySide6.QtCore import QObject, QSettings, QStandardPaths, QTranslator, QUrl, Signal, Slot
from PySide6.QtGui import QIcon
from PySide6.QtQml import QQmlApplicationEngine, qmlRegisterSingletonType, qmlRegisterType
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtWidgets import QApplication, QMessageBox
from sqlalchemy import Engine
from sqlalchemy.engine import Connection

from src.app import resources_rc  # noqa: F401  # registers Qt resource bundle
from src.app.bundle_paths import runtime_root
from src.app.identity import (
    APPLICATION_NAME,
    CRASH_LOG_FILENAME,
    CRASH_LOGGER_NAME,
    DISPLAY_NAME_DESKTOP,
    ORGANIZATION_NAME,
    QML_MODULE_URI,
    QML_MODULE_VERSION_MAJOR,
    QML_MODULE_VERSION_MINOR,
    RUNTIME_ARGV_NAME,
)
from src.app.identity_migration import migrate_legacy_identity
from src.app.macos_window import present_main_window
from src.app.models.entry_list_model import EntryListModel
from src.app.models.exchange_rate_list_model import ExchangeRateListModel
from src.app.models.snapshot_list_model import SnapshotListModel
from src.app.models.suggestion_list_model import SuggestionListModel
from src.app.viewmodels.app_vm import AppViewModel
from src.app.viewmodels.audit_log_vm import AuditLogViewModel
from src.app.viewmodels.currency_vm import CurrencyViewModel
from src.app.viewmodels.entries_vm import EntriesViewModel
from src.app.viewmodels.import_vm import ImportViewModel
from src.app.viewmodels.methodology_vm import MethodologyViewModel
from src.app.viewmodels.plan_import_vm import PlanImportViewModel
from src.app.viewmodels.plan_vm import PlanViewModel
from src.app.viewmodels.settings_vm import SettingsViewModel
from src.app.viewmodels.simulation_vm import SimulationViewModel
from src.app.viewmodels.suggestions_vm import SuggestionsViewModel
from src.data.database import create_engine_for_path, resolve_database_path
from src.data.migrate import run_migrations as apply_migrations
from src.data.repositories.audit_log_repo import SqliteAuditLogRepository
from src.data.repositories.entry_repo import SqliteEntryRepository
from src.data.repositories.exchange_rate_repo import SqliteExchangeRateRepository
from src.data.repositories.expense_dictionary_repo import (
    SqliteExpenseCategoryRepository,
    SqliteExpenseNameRepository,
    SqliteExpensePlaceRepository,
)
from src.data.repositories.plan_repo import SqlitePlanRepository
from src.data.repositories.recorded_expense_repo import SqliteRecordedExpenseRepository
from src.data.repositories.simulation_run_repo import SqliteSimulationRunRepository
from src.export.plan_exporter import PlanExporter
from src.integrations.exchange_rate_fetcher import configure_dev_mode
from src.integrations.plan_import_service import PlanImportService

ROOT_DIR = runtime_root()
QML_DIR = ROOT_DIR / "qml"
QML_MAIN = QML_DIR / "main.qml"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=DISPLAY_NAME_DESKTOP)
    parser.add_argument(
        "--dev",
        action="store_true",
        help="Enable developer features: QML hot-reload and mock exchange-rate provider",
    )
    return parser.parse_args(argv)


def run_migrations(db_path: Path) -> None:
    """Apply Alembic migrations to the database at *db_path*."""
    apply_migrations(db_path=db_path)


def app_data_directory() -> Path:
    location = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation)
    if not location:
        msg = "Could not resolve application data directory"
        raise RuntimeError(msg)
    data_dir = Path(location)
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def configure_crash_logger() -> logging.Logger:
    log_path = app_data_directory() / CRASH_LOG_FILENAME
    logger = logging.getLogger(CRASH_LOGGER_NAME)
    logger.setLevel(logging.ERROR)
    logger.handlers.clear()
    handler = RotatingFileHandler(log_path, maxBytes=1_000_000, backupCount=3)
    handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s %(message)s"),
    )
    logger.addHandler(handler)
    return logger


def install_exception_hook(app: QApplication, crash_logger: logging.Logger) -> None:
    previous_hook = sys.excepthook

    def exception_hook(
        exc_type: type[BaseException], exc_value: BaseException, exc_tb: object
    ) -> None:
        formatted = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
        crash_logger.error("Unhandled exception:\n%s", formatted)

        message = QMessageBox()
        message.setIcon(QMessageBox.Icon.Critical)
        message.setWindowTitle("Unexpected Error")
        message.setText("Cash Flow Planner encountered an unexpected error.")
        message.setInformativeText(str(exc_value))
        message.setDetailedText(formatted)
        message.setStandardButtons(
            QMessageBox.StandardButton.Retry | QMessageBox.StandardButton.Close,
        )
        message.setDefaultButton(QMessageBox.StandardButton.Retry)
        choice = message.exec()

        if choice == QMessageBox.StandardButton.Retry:
            app.quit()
            os.execv(sys.executable, [sys.executable, *sys.argv[1:]])
            return

        previous_hook(exc_type, exc_value, exc_tb)

    sys.excepthook = exception_hook


class QmlReloader(QObject):
    """Reload the root QML component on the main thread."""

    reload_requested = Signal()

    def __init__(
        self, engine: QQmlApplicationEngine, qml_path: Path, parent: QObject | None = None
    ) -> None:
        super().__init__(parent)
        self._engine = engine
        self._qml_path = qml_path
        self.reload_requested.connect(self._reload)

    @Slot()
    def _reload(self) -> None:
        for root_object in self._engine.rootObjects():
            root_object.deleteLater()
        self._engine.clearComponentCache()
        self._engine.load(QUrl.fromLocalFile(str(self._qml_path)))


def start_qml_watcher(qml_dir: Path, reloader: QmlReloader) -> object:
    from watchdog.events import FileSystemEvent, FileSystemEventHandler
    from watchdog.observers import Observer

    class QmlWatchHandler(FileSystemEventHandler):
        def on_modified(self, event: FileSystemEvent) -> None:
            if event.is_directory:
                return
            if Path(event.src_path).suffix != ".qml":
                return
            reloader.reload_requested.emit()

    observer = Observer()
    observer.schedule(QmlWatchHandler(), str(qml_dir), recursive=True)
    observer.start()
    return observer


def load_qml(engine: QQmlApplicationEngine, qml_path: Path) -> None:
    if not qml_path.is_file():
        msg = f"QML entry point not found: {qml_path}"
        raise FileNotFoundError(msg)
    engine.load(QUrl.fromLocalFile(str(qml_path)))


def _read_language_setting() -> str:
    lang_value = QSettings().value("language", "en")
    if isinstance(lang_value, str) and lang_value:
        return lang_value
    return "en"


def _install_translator(app: QApplication, lang: str) -> QTranslator:
    translator = QTranslator(app)
    qm_path = f":/i18n/app_{lang}.qm"
    if translator.load(qm_path):
        app.installTranslator(translator)
    return translator


def register_qml_singletons() -> None:
    theme_tokens_path = QML_DIR / "components" / "ThemeTokens.qml"
    qmlRegisterSingletonType(  # type: ignore[call-overload]
        QUrl.fromLocalFile(str(theme_tokens_path)),
        "ThemeTokens",
        1,
        0,
        "ThemeTokens",
    )


def register_qml_types() -> None:
    register_qml_singletons()
    qmlRegisterType(  # type: ignore[call-overload]
        EntryListModel,
        QML_MODULE_URI,
        QML_MODULE_VERSION_MAJOR,
        QML_MODULE_VERSION_MINOR,
        "EntryListModel",
    )
    qmlRegisterType(  # type: ignore[call-overload]
        SnapshotListModel,
        QML_MODULE_URI,
        QML_MODULE_VERSION_MAJOR,
        QML_MODULE_VERSION_MINOR,
        "SnapshotListModel",
    )
    qmlRegisterType(  # type: ignore[call-overload]
        ExchangeRateListModel,
        QML_MODULE_URI,
        QML_MODULE_VERSION_MAJOR,
        QML_MODULE_VERSION_MINOR,
        "ExchangeRateListModel",
    )
    qmlRegisterType(  # type: ignore[call-overload]
        SuggestionListModel,
        QML_MODULE_URI,
        QML_MODULE_VERSION_MAJOR,
        QML_MODULE_VERSION_MINOR,
        "SuggestionListModel",
    )


def bootstrap_view_models(
    db_path: Path,
) -> tuple[
    PlanViewModel,
    EntriesViewModel,
    SimulationViewModel,
    SuggestionsViewModel,
    ImportViewModel,
    PlanImportViewModel,
    CurrencyViewModel,
    AuditLogViewModel,
    Engine,
    Connection,
]:
    """Construct repositories and ViewModels backed by a persistent DB connection."""
    db_engine = create_engine_for_path(db_path)
    db_conn = db_engine.connect().execution_options(isolation_level="AUTOCOMMIT")

    audit_log_repo = SqliteAuditLogRepository(db_conn)
    plan_repo = SqlitePlanRepository(db_conn, audit_log_repo)
    entry_repo = SqliteEntryRepository(db_conn, audit_log_repo)
    exchange_rate_repo = SqliteExchangeRateRepository(db_conn)
    _ = SqliteSimulationRunRepository(db_conn)
    _ = SqliteExpenseNameRepository(db_conn)
    _ = SqliteExpenseCategoryRepository(db_conn)
    _ = SqliteExpensePlaceRepository(db_conn)
    _ = SqliteRecordedExpenseRepository(db_conn)

    plan_vm = PlanViewModel(
        plan_repo,
        PlanExporter(plan_repo, entry_repo, exchange_rate_repo),
        entry_repo,
    )
    entries_vm = EntriesViewModel(entry_repo)
    suggestions_vm = SuggestionsViewModel(entry_repo)
    simulation_vm = SimulationViewModel(entry_repo, exchange_rate_repo, suggestions_vm)
    import_vm = ImportViewModel(entry_repo)
    plan_import_vm = PlanImportViewModel(
        PlanImportService(plan_repo, entry_repo, exchange_rate_repo, db_conn)
    )
    currency_vm = CurrencyViewModel(exchange_rate_repo)
    audit_log_vm = AuditLogViewModel(audit_log_repo)

    return (
        plan_vm,
        entries_vm,
        simulation_vm,
        suggestions_vm,
        import_vm,
        plan_import_vm,
        currency_vm,
        audit_log_vm,
        db_engine,
        db_conn,
    )


def main(argv: list[str] | None = None) -> int:
    runtime_argv = sys.argv if argv is None else [RUNTIME_ARGV_NAME, *argv]
    args = parse_args(runtime_argv[1:])
    configure_dev_mode(enabled=args.dev)

    QApplication.setOrganizationName(ORGANIZATION_NAME)
    QApplication.setApplicationName(APPLICATION_NAME)

    app = QApplication(runtime_argv)
    migrate_legacy_identity()
    app.setWindowIcon(QIcon(":/icons/app-icon.svg"))
    QSettings()

    crash_logger = configure_crash_logger()
    install_exception_hook(app, crash_logger)

    db_path = resolve_database_path()
    run_migrations(db_path)

    QQuickStyle.setStyle("Material")
    register_qml_types()

    settings_vm = SettingsViewModel()
    methodology_vm = MethodologyViewModel()
    translator = _install_translator(app, _read_language_setting())

    (
        plan_vm,
        entries_vm,
        simulation_vm,
        suggestions_vm,
        import_vm,
        plan_import_vm,
        currency_vm,
        audit_log_vm,
        db_engine,
        db_conn,
    ) = bootstrap_view_models(db_path)

    engine = QQmlApplicationEngine()
    app_vm = AppViewModel()
    root_context = engine.rootContext()
    root_context.setContextProperty("appViewModel", app_vm)
    root_context.setContextProperty("settingsViewModel", settings_vm)
    root_context.setContextProperty("methodologyViewModel", methodology_vm)
    root_context.setContextProperty("planViewModel", plan_vm)
    root_context.setContextProperty("entriesViewModel", entries_vm)
    root_context.setContextProperty("simulationViewModel", simulation_vm)
    root_context.setContextProperty("suggestionsViewModel", suggestions_vm)
    root_context.setContextProperty("importViewModel", import_vm)
    root_context.setContextProperty("planImportViewModel", plan_import_vm)
    root_context.setContextProperty("ratesViewModel", currency_vm)
    root_context.setContextProperty("auditLogViewModel", audit_log_vm)

    def on_language_changed() -> None:
        nonlocal translator
        app.removeTranslator(translator)
        translator = _install_translator(app, _read_language_setting())
        engine.retranslate()
        for vm in (
            plan_vm,
            entries_vm,
            simulation_vm,
            suggestions_vm,
            import_vm,
            plan_import_vm,
            currency_vm,
            audit_log_vm,
            methodology_vm,
        ):
            vm.retranslate()

    settings_vm.languageChanged.connect(on_language_changed)

    for vm in (
        app_vm,
        settings_vm,
        methodology_vm,
        plan_vm,
        entries_vm,
        simulation_vm,
        suggestions_vm,
        import_vm,
        plan_import_vm,
        currency_vm,
        audit_log_vm,
    ):
        vm.setParent(engine)

    qml_observer: object | None = None
    try:
        if args.dev:
            reloader = QmlReloader(engine, QML_MAIN)
            qml_observer = start_qml_watcher(QML_DIR, reloader)

        load_qml(engine, QML_MAIN)
        if not engine.rootObjects():
            return 1

        present_main_window(engine)
        exit_code = app.exec()
    finally:
        if qml_observer is not None:
            qml_observer.stop()  # type: ignore[attr-defined]
            qml_observer.join()  # type: ignore[attr-defined]
        db_conn.close()
        db_engine.dispose()

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
