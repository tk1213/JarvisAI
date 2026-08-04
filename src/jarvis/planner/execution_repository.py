from __future__ import annotations

import json
from dataclasses import asdict
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import text

from jarvis.database.db import DatabaseManager
from jarvis.planner.execution_record import (
    ExecutionEventRecord,
    PlanExecutionRecord,
    StepExecutionRecord,
)


class PlanExecutionRepository:
    def __init__(
        self,
        database: DatabaseManager,
    ) -> None:
        self._database = database

    async def startup(self) -> None:
        async with self._database.engine.begin() as connection:
            await connection.execute(
                text(
                    """
                    CREATE TABLE IF NOT EXISTS plan_execution_records (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        goal TEXT NOT NULL,
                        plan_status TEXT NOT NULL,
                        success INTEGER NOT NULL,
                        completed_steps INTEGER NOT NULL,
                        steps_json TEXT NOT NULL,
                        events_json TEXT NOT NULL,
                        created_at TEXT NOT NULL
                    )
                    """
                )
            )

    async def save(
        self,
        record: PlanExecutionRecord,
    ) -> int:
        steps_json = json.dumps(
            [
                asdict(step)
                for step in record.steps
            ],
            ensure_ascii=False,
            default=self._json_default,
        )

        events_json = json.dumps(
            [
                asdict(event)
                for event in record.events
            ],
            ensure_ascii=False,
            default=self._json_default,
        )

        async with self._database.engine.begin() as connection:
            result = await connection.execute(
                text(
                    """
                    INSERT INTO plan_execution_records (
                        goal,
                        plan_status,
                        success,
                        completed_steps,
                        steps_json,
                        events_json,
                        created_at
                    )
                    VALUES (
                        :goal,
                        :plan_status,
                        :success,
                        :completed_steps,
                        :steps_json,
                        :events_json,
                        :created_at
                    )
                    """
                ),
                {
                    "goal": record.goal,
                    "plan_status": record.plan_status,
                    "success": 1 if record.success else 0,
                    "completed_steps": record.completed_steps,
                    "steps_json": steps_json,
                    "events_json": events_json,
                    "created_at": datetime.now(UTC).isoformat(),
                },
            )

            record_id = result.lastrowid

        if record_id is None:
            raise RuntimeError(
                "Database did not return an execution record id."
            )

        return int(
            record_id
        )

    async def get(
        self,
        record_id: int,
    ) -> PlanExecutionRecord | None:
        if record_id < 1:
            raise ValueError(
                "record_id must be at least 1."
            )

        async with self._database.engine.connect() as connection:
            result = await connection.execute(
                text(
                    """
                    SELECT
                        goal,
                        plan_status,
                        success,
                        completed_steps,
                        steps_json,
                        events_json
                    FROM plan_execution_records
                    WHERE id = :record_id
                    """
                ),
                {
                    "record_id": record_id,
                },
            )

            row = result.mappings().first()

        if row is None:
            return None

        return self._record_from_row(
            row
        )

    async def list_recent(
        self,
        *,
        limit: int = 20,
    ) -> list[PlanExecutionRecord]:
        if limit < 1:
            raise ValueError(
                "limit must be at least 1."
            )

        async with self._database.engine.connect() as connection:
            result = await connection.execute(
                text(
                    """
                    SELECT
                        goal,
                        plan_status,
                        success,
                        completed_steps,
                        steps_json,
                        events_json
                    FROM plan_execution_records
                    ORDER BY id DESC
                    LIMIT :limit
                    """
                ),
                {
                    "limit": limit,
                },
            )

            rows = result.mappings().all()

        return [
            self._record_from_row(
                row
            )
            for row in rows
        ]

    @classmethod
    def _record_from_row(
        cls,
        row: Any,
    ) -> PlanExecutionRecord:
        steps_data = json.loads(
            row["steps_json"]
        )
        events_data = json.loads(
            row["events_json"]
        )

        return PlanExecutionRecord(
            goal=row["goal"],
            plan_status=row["plan_status"],
            success=bool(
                row["success"]
            ),
            completed_steps=int(
                row["completed_steps"]
            ),
            steps=tuple(
                StepExecutionRecord(
                    **step
                )
                for step in steps_data
            ),
            events=tuple(
                ExecutionEventRecord(
                    sequence=event["sequence"],
                    event_type=event["event_type"],
                    timestamp=datetime.fromisoformat(
                        event["timestamp"]
                    ),
                    step_index=event["step_index"],
                    capability=event["capability"],
                    attempt=event["attempt"],
                    details=event["details"],
                )
                for event in events_data
            ),
        )

    @staticmethod
    def _json_default(
        value: Any,
    ) -> Any:
        if isinstance(
            value,
            datetime,
        ):
            return value.isoformat()

        raise TypeError(
            "Object is not JSON serializable: "
            f"{type(value).__name__}"
        )
