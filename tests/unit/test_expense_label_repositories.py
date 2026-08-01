from __future__ import annotations

import pytest
from sqlalchemy.engine import Connection

from src.data.repositories.expense_dictionary_repo import SqliteExpenseNameRepository


@pytest.fixture
def name_repository(db_conn: Connection) -> SqliteExpenseNameRepository:
    return SqliteExpenseNameRepository(db_conn)


def test_search_empty_prefix_returns_empty_list(
    db_conn: Connection,
    name_repository: SqliteExpenseNameRepository,
) -> None:
    name_repository.get_or_create("Netflix")
    db_conn.commit()

    assert name_repository.search("", limit=10) == []
    assert name_repository.search("   ", limit=10) == []


def test_search_respects_limit(
    db_conn: Connection,
    name_repository: SqliteExpenseNameRepository,
) -> None:
    for label in ("Alpha Mart", "Apricot Stand", "Avocado Bar", "Beta Shop"):
        name_repository.get_or_create(label)
    db_conn.commit()

    matches = name_repository.search("a", limit=2)

    assert len(matches) == 2
    assert [match.label for match in matches] == ["Alpha Mart", "Apricot Stand"]


def test_search_orders_alphabetically_case_insensitive(
    db_conn: Connection,
    name_repository: SqliteExpenseNameRepository,
) -> None:
    for label in ("Spotify", "shell", "Safari"):
        name_repository.get_or_create(label)
    db_conn.commit()

    matches = name_repository.search("s", limit=10)

    assert [match.label for match in matches] == ["Safari", "shell", "Spotify"]
