from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import text

from jarvis.database.db import DatabaseManager
from jarvis.memory.audit import (
    MemoryAuditAction,
    MemoryAuditEvent,
)


class MemoryAuditRepository:
    def __init__(
        self,
        database: DatabaseManager,
    ) -> None:
        self._database = database
        self._schema_ready = False

    async def append(
        self,
        event: MemoryAuditEvent,
    ) -> None:
        await self._ensure_schema()

        async with self._database.engine.begin() as connection:
            await connection.execute(
                text(
                    """
                    INSERT INTO memory_audit (
                        action,
                        key,
                        value,
                        source,
                        reason,
                        created_at
                    )
                    VALUES (
                        :action,
                        :key,
                        :value,
                        :source,
                        :reason,
                        :created_at
                    )
                    """
                ),
                {
                    "action": event.action.value,
                    "key": event.key,
                    "value": event.value,
                    "source": event.source,
                    "reason": event.reason,
                    "created_at": event.created_at.isoformat(),
                },
            )

    async def list_recent(
        self,
        *,
        limit: int = 50,
    ) -> list[MemoryAuditEvent]:
        if limit < 1:
            raise ValueError(
                "limit must be at least 1."
            )

        await self._ensure_schema()

        async with self._database.engine.connect() as connection:
            result = await connection.execute(
                text(
                    """
                    SELECT
                        action,
                        key,
                        value,
                        source,
                        reason,
                        created_at
                    FROM memory_audit
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
            self._row_to_event(
                dict(row)
            )
            for row in rows
        ]

    async def _ensure_schema(
        self,
    ) -> None:
        if self._schema_ready:
            return

        async with self._database.engine.begin() as connection:
            await connection.exec_driver_sql(
                """
                CREATE TABLE IF NOT EXISTS memory_audit (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    action TEXT NOT NULL,
                    key TEXT NOT NULL,
                    value TEXT,
                    source TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )

            await connection.exec_driver_sql(
                """
                CREATE INDEX IF NOT EXISTS
                    ix_memory_audit_created_at
                ON memory_audit(created_at)
                """
            )

            await connection.exec_driver_sql(
                """
                CREATE INDEX IF NOT EXISTS
                    ix_memory_audit_key
                ON memory_audit(key)
                """
            )

        self._schema_ready = True

    @staticmethod
    def _row_to_event(
        row: dict[str, Any],
    ) -> MemoryAuditEvent:
        created_at = datetime.fromisoformat(
            str(
                row["created_at"]
            )
        )

        if created_at.tzinfo is None:
            created_at = created_at.replace(
                tzinfo=UTC
            )

        return MemoryAuditEvent(
            action=MemoryAuditAction(
                str(
                    row["action"]
                )
            ),
            key=str(
                row["key"]
            ),
            value=(
                None
                if row["value"] is None
                else str(
                    row["value"]
                )
            ),
            source=str(
                row["source"]
            ),
            reason=str(
                row["reason"]
            ),
            created_at=created_at,
        )
