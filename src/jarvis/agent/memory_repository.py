from __future__ import annotations

import json
from datetime import datetime

from sqlalchemy import text
from sqlalchemy.engine import RowMapping

from jarvis.database.db import DatabaseManager
from jarvis.planner.ai_plan_memory import AIPlanMemoryRecord


class AIAgentMemoryRepository:
    def __init__(
        self,
        database: DatabaseManager,
    ) -> None:
        self._database = database

    async def add(
        self,
        record: AIPlanMemoryRecord,
    ) -> int:
        sql = text(
            """
            INSERT INTO agent_plan_memories (
                goal,
                capabilities_json,
                success,
                completed_steps,
                failed_steps,
                reflection_decision,
                created_at,
                metadata_json
            )
            VALUES (
                :goal,
                :capabilities_json,
                :success,
                :completed_steps,
                :failed_steps,
                :reflection_decision,
                :created_at,
                :metadata_json
            )
            """
        )

        async with self._database.session() as session:
            result = await session.execute(
                sql,
                {
                    "goal": record.goal,
                    "capabilities_json": json.dumps(
                        list(record.capabilities),
                        ensure_ascii=False,
                    ),
                    "success": int(record.success),
                    "completed_steps": record.completed_steps,
                    "failed_steps": record.failed_steps,
                    "reflection_decision": record.reflection_decision,
                    "created_at": record.created_at.isoformat(),
                    "metadata_json": json.dumps(
                        record.metadata,
                        ensure_ascii=False,
                        default=str,
                    ),
                },
            )

            inserted_id = result.lastrowid

        if inserted_id is None:
            raise RuntimeError(
                "Database did not return the inserted agent memory ID."
            )

        return int(inserted_id)

    async def list_recent(
        self,
        *,
        limit: int = 500,
    ) -> tuple[AIPlanMemoryRecord, ...]:
        if limit < 1:
            raise ValueError(
                "limit must be at least 1."
            )

        sql = text(
            """
            SELECT
                goal,
                capabilities_json,
                success,
                completed_steps,
                failed_steps,
                reflection_decision,
                created_at,
                metadata_json
            FROM agent_plan_memories
            ORDER BY id DESC
            LIMIT :limit
            """
        )

        async with self._database.session() as session:
            result = await session.execute(
                sql,
                {
                    "limit": limit,
                },
            )

            rows = result.mappings().all()

        return tuple(
            self._row_to_record(row)
            for row in rows
        )

    async def count(
        self,
    ) -> int:
        sql = text(
            """
            SELECT COUNT(*) AS total
            FROM agent_plan_memories
            """
        )

        async with self._database.session() as session:
            result = await session.execute(
                sql
            )

            row = result.mappings().first()

        if row is None:
            return 0

        return int(
            row["total"]
        )

    async def delete_oldest(
        self,
        *,
        keep: int,
    ) -> int:
        if keep < 0:
            raise ValueError(
                "keep cannot be negative."
            )

        sql = text(
            """
            DELETE FROM agent_plan_memories
            WHERE id NOT IN (
                SELECT id
                FROM agent_plan_memories
                ORDER BY id DESC
                LIMIT :keep
            )
            """
        )

        async with self._database.session() as session:
            result = await session.execute(
                sql,
                {
                    "keep": keep,
                },
            )

            affected_rows = result.rowcount

        return int(
            affected_rows or 0
        )

    @staticmethod
    def _row_to_record(
        row: RowMapping,
    ) -> AIPlanMemoryRecord:
        capabilities = json.loads(
            str(row["capabilities_json"])
        )
        metadata = json.loads(
            str(row["metadata_json"])
        )

        if not isinstance(capabilities, list):
            raise TypeError(
                "Stored agent memory capabilities must be a JSON list."
            )

        if not isinstance(metadata, dict):
            raise TypeError(
                "Stored agent memory metadata must be a JSON object."
            )

        return AIPlanMemoryRecord(
            goal=str(row["goal"]),
            capabilities=tuple(
                str(item)
                for item in capabilities
            ),
            success=bool(
                row["success"]
            ),
            completed_steps=int(
                row["completed_steps"]
            ),
            failed_steps=int(
                row["failed_steps"]
            ),
            reflection_decision=str(
                row["reflection_decision"]
            ),
            created_at=AIAgentMemoryRepository._parse_datetime(
                row["created_at"]
            ),
            metadata=dict(
                metadata
            ),
        )

    @staticmethod
    def _parse_datetime(
        value: object,
    ) -> datetime:
        if isinstance(
            value,
            datetime,
        ):
            return value

        return datetime.fromisoformat(
            str(value)
        )
