from __future__ import annotations

from dataclasses import dataclass

from jarvis.planner.execution_persistence import (
    ExecutionPersistenceService,
)
from jarvis.planner.execution_query import ExecutionQuery
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
        return await self.query(
            ExecutionQuery(
                limit=limit,
            )
        )

    async def query(
        self,
        query: ExecutionQuery,
    ) -> ExecutionHistorySummary:
        records = await self._persistence.list_recent(
            limit=query.limit
        )

        filtered = [
            record
            for record in records
            if self._matches(
                record,
                query=query,
            )
        ]

        completed = sum(
            record.success
            for record in filtered
        )

        failed = len(
            filtered
        ) - completed

        return ExecutionHistorySummary(
            total=len(
                filtered
            ),
            completed=completed,
            failed=failed,
            records=tuple(
                filtered
            ),
        )

    async def get(
        self,
        record_id: int,
    ) -> PlanExecutionRecord | None:
        return await self._persistence.get(
            record_id
        )

    @staticmethod
    def _matches(
        record: PlanExecutionRecord,
        *,
        query: ExecutionQuery,
    ) -> bool:
        if (
            query.status is not None
            and record.plan_status.lower()
            != query.status
        ):
            return False

        if query.capability is not None:
            capabilities = {
                step.capability
                for step in record.steps
            }

            if query.capability not in capabilities:
                return False

        return True
