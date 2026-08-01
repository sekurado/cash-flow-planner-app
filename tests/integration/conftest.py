from __future__ import annotations

import pytest
from sqlalchemy.engine import Connection

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


@pytest.fixture
def audit_log_repository(db_conn: Connection) -> SqliteAuditLogRepository:
    return SqliteAuditLogRepository(db_conn)


@pytest.fixture
def plan_repository(
    db_conn: Connection,
    audit_log_repository: SqliteAuditLogRepository,
) -> SqlitePlanRepository:
    return SqlitePlanRepository(db_conn, audit_log_repository)


@pytest.fixture
def entry_repository(
    db_conn: Connection,
    audit_log_repository: SqliteAuditLogRepository,
) -> SqliteEntryRepository:
    return SqliteEntryRepository(db_conn, audit_log_repository)


@pytest.fixture
def exchange_rate_repository(db_conn: Connection) -> SqliteExchangeRateRepository:
    return SqliteExchangeRateRepository(db_conn)


@pytest.fixture
def simulation_run_repository(db_conn: Connection) -> SqliteSimulationRunRepository:
    return SqliteSimulationRunRepository(db_conn)


@pytest.fixture
def expense_name_repository(db_conn: Connection) -> SqliteExpenseNameRepository:
    return SqliteExpenseNameRepository(db_conn)


@pytest.fixture
def expense_category_repository(db_conn: Connection) -> SqliteExpenseCategoryRepository:
    return SqliteExpenseCategoryRepository(db_conn)


@pytest.fixture
def expense_place_repository(db_conn: Connection) -> SqliteExpensePlaceRepository:
    return SqliteExpensePlaceRepository(db_conn)


@pytest.fixture
def recorded_expense_repository(db_conn: Connection) -> SqliteRecordedExpenseRepository:
    return SqliteRecordedExpenseRepository(db_conn)
