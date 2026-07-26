from __future__ import annotations

from datetime import UTC, datetime
from typing import Protocol

from pydantic import BaseModel
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.engine import Connection, RowMapping

from src.data.schema import exchange_rates
from src.domain.entities import ExchangeRate


class ExchangeRateUpsertDto(BaseModel):
    from_currency: str
    to_currency: str
    rate: float
    updated_at: str


class AbstractExchangeRateRepository(Protocol):
    def get_all(self) -> list[ExchangeRate]: ...

    def upsert(self, dto: ExchangeRateUpsertDto) -> ExchangeRate: ...

    def delete(self, from_currency: str, to_currency: str) -> None: ...

    def delete_all(self) -> None: ...


def _row_to_exchange_rate(row: RowMapping) -> ExchangeRate:
    return ExchangeRate.model_validate(dict(row))


class SqliteExchangeRateRepository:
    def __init__(self, conn: Connection) -> None:
        self._conn = conn

    def get_all(self) -> list[ExchangeRate]:
        stmt = exchange_rates.select().order_by(
            exchange_rates.c.from_currency.asc(),
            exchange_rates.c.to_currency.asc(),
        )
        rows = self._conn.execute(stmt).mappings().all()
        return [_row_to_exchange_rate(row) for row in rows]

    def upsert(self, dto: ExchangeRateUpsertDto) -> ExchangeRate:
        stmt = sqlite_insert(exchange_rates).values(
            from_currency=dto.from_currency,
            to_currency=dto.to_currency,
            rate=dto.rate,
            updated_at=dto.updated_at,
        )
        stmt = stmt.on_conflict_do_update(
            index_elements=["from_currency", "to_currency"],
            set_={
                "rate": stmt.excluded.rate,
                "updated_at": stmt.excluded.updated_at,
            },
        )
        self._conn.execute(stmt)
        row = (
            self._conn.execute(
                exchange_rates.select().where(
                    exchange_rates.c.from_currency == dto.from_currency,
                    exchange_rates.c.to_currency == dto.to_currency,
                )
            )
            .mappings()
            .one()
        )
        return _row_to_exchange_rate(row)

    def delete(self, from_currency: str, to_currency: str) -> None:
        self._conn.execute(
            exchange_rates.delete().where(
                exchange_rates.c.from_currency == from_currency,
                exchange_rates.c.to_currency == to_currency,
            )
        )

    def delete_all(self) -> None:
        self._conn.execute(exchange_rates.delete())

    @staticmethod
    def utc_now_iso() -> str:
        return datetime.now(tz=UTC).replace(microsecond=0).isoformat()
