from __future__ import annotations

import asyncio

from jarvis.planner.execution_record import (
    PlanExecutionRecord,
    PlanExecutionRecordBuilder,
)
from jarvis.planner.execution_repository import (
    PlanExecutionRepository,
)
from jarvis.planner.executor import PlanExecutionResult


class ExecutionPersistenceService:
    def __init__(
        self,
        repository: PlanExecutionRepository,
        *,
        record_builder: PlanExecutionRecordBuilder | None = None,
    ) -> None:
        self._repository = repository
        self._record_builder = (
            record_builder
            if record_builder is not None
            else PlanExecutionRecordBuilder()
        )
        self._started = False
        self._startup_lock = asyncio.Lock()

    @property
    def started(self) -> bool:
        return self._started

    async def startup(self) -> None:
        if self._started:
            return

        async with self._startup_lock:
            if self._started:
                return

            await self._repository.startup()
            self._started = True

    async def persist_execution(
        self,
        execution: PlanExecutionResult,
    ) -> int:
        await self.startup()

        record = self._record_builder.build(
            execution
        )

        return await self._repository.save(
            record
        )

    async def get(
        self,
        record_id: int,
    ) -> PlanExecutionRecord | None:
        await self.startup()

        return await self._repository.get(
            record_id
        )

    async def list_recent(
        self,
        *,
        limit: int = 20,
    ) -> list[PlanExecutionRecord]:
        await self.startup()

        return await self._repository.list_recent(
            limit=limit
        )
