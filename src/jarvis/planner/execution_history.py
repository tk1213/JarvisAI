from __future__ import annotations

from dataclasses import dataclass

from jarvis.planner.execution_persistence import (
    ExecutionPersistenceService,
)
from jarvis.planner.execution_record import (
    PlanExecutionRecord,
)


@dataclass(slots=True, frozen=True)
class ExecutionHistorySummary:
    total: int
    completed: int
    failed: int
    records: tuple[PlanExecutionRecord, ...]


class ExecutionHistoryService:
    def __init__(
        self,
        persistence: ExecutionPersistenceService,
    ) -> None:
        self._persistence = persistence

    async def recent(
        self,
        *,
        limit: int = 20,
    ) -> ExecutionHistorySummary:
        if limit < 1:
            raise ValueError(
                "limit must be at least 1."
            )

        records = await self._persistence.list_recent(
            limit=limit
        )

        completed = sum(
            record.success
            for record in records
        )

        failed = len(
            records
        ) - completed

        return ExecutionHistorySummary(
            total=len(
                records
            ),
            completed=completed,
            failed=failed,
            records=tuple(
                records
            ),
        )

    async def get(
        self,
        record_id: int,
    ) -> PlanExecutionRecord | None:
        return await self._persistence.get(
            record_id
        )
