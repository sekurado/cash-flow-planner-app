from __future__ import annotations

import pytest
from sqlalchemy.engine import Connection

from src.data.repositories.audit_log_repo import SqliteAuditLogRepository
from src.data.repositories.entry_repo import SqliteEntryRepository
from src.data.repositories.exchange_rate_repo import SqliteExchangeRateRepository
from src.data.repositories.plan_repo import SqlitePlanRepository
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
