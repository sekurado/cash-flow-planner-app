from __future__ import annotations

import base64
import uuid
import zlib
from datetime import UTC, date, datetime
from typing import Any, Protocol

from pydantic import BaseModel
from sqlalchemy import delete, insert, select
from sqlalchemy.engine import Connection, RowMapping

from src.data.schema import simulation_runs
from src.domain.entities import SimulationRun


class SimulationRunCreateDto(BaseModel):
    plan_id: str
    start_date: date
    end_date: date
    result_json: str


class AbstractSimulationRunRepository(Protocol):
    def find_by_plan_id(self, plan_id: str) -> list[SimulationRun]: ...

    def find_latest(self, plan_id: str) -> SimulationRun | None: ...

    def create(self, dto: SimulationRunCreateDto) -> SimulationRun: ...

    def delete(self, run_id: str) -> None: ...


def _utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _compress_result_json(result_json: str) -> str:
    compressed = zlib.compress(result_json.encode("utf-8"))
    return base64.b64encode(compressed).decode("ascii")


def _decompress_result_json(stored: str) -> str:
    compressed = base64.b64decode(stored.encode("ascii"))
    return zlib.decompress(compressed).decode("utf-8")


def _row_to_simulation_run(row: RowMapping) -> SimulationRun:
    data: dict[str, Any] = dict(row)
    if "start_date" in data:
        data["start_date"] = date.fromisoformat(data["start_date"])
    if "end_date" in data:
        data["end_date"] = date.fromisoformat(data["end_date"])
    if "result_json" in data:
        data["result_json"] = _decompress_result_json(data["result_json"])
    return SimulationRun.model_validate(data)


class SqliteSimulationRunRepository:
    def __init__(self, conn: Connection) -> None:
        self._conn = conn

    def find_by_plan_id(self, plan_id: str) -> list[SimulationRun]:
        stmt = (
            select(simulation_runs)
            .where(simulation_runs.c.plan_id == plan_id)
            .order_by(simulation_runs.c.created_at.asc())
        )
        rows = self._conn.execute(stmt).mappings().all()
        return [_row_to_simulation_run(row) for row in rows]

    def find_latest(self, plan_id: str) -> SimulationRun | None:
        stmt = (
            select(simulation_runs)
            .where(simulation_runs.c.plan_id == plan_id)
            .order_by(simulation_runs.c.created_at.desc())
            .limit(1)
        )
        row = self._conn.execute(stmt).mappings().one_or_none()
        if row is None:
            return None
        return _row_to_simulation_run(row)

    def find_by_id(self, run_id: str) -> SimulationRun | None:
        stmt = select(simulation_runs).where(simulation_runs.c.id == run_id)
        row = self._conn.execute(stmt).mappings().one_or_none()
        if row is None:
            return None
        return _row_to_simulation_run(row)

    def create(self, dto: SimulationRunCreateDto) -> SimulationRun:
        now = _utc_now_iso()
        run_id = str(uuid.uuid4())
        self._conn.execute(
            insert(simulation_runs).values(
                id=run_id,
                plan_id=dto.plan_id,
                start_date=dto.start_date.isoformat(),
                end_date=dto.end_date.isoformat(),
                result_json=_compress_result_json(dto.result_json),
                created_at=now,
            )
        )
        run = self.find_by_id(run_id)
        assert run is not None
        return run

    def delete(self, run_id: str) -> None:
        self._conn.execute(delete(simulation_runs).where(simulation_runs.c.id == run_id))
