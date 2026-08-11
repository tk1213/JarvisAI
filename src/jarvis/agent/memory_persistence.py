from __future__ import annotations

from jarvis.agent.memory_repository import AIAgentMemoryRepository
from jarvis.agent.memory_retention import (
    AIAgentMemoryRetentionPolicy,
    AIAgentMemoryRetentionResult,
)
from jarvis.planner.ai_plan_memory import (
    AIPlanMemoryRecord,
    AIPlanMemoryStore,
)


class AIAgentMemoryPersistence:
    def __init__(
        self,
        *,
        repository: AIAgentMemoryRepository,
        store: AIPlanMemoryStore,
        restore_limit: int = 500,
        retention: AIAgentMemoryRetentionPolicy | None = None,
    ) -> None:
        if restore_limit < 1:
            raise ValueError(
                "restore_limit must be at least 1."
            )

        self._repository = repository
        self._store = store
        self._restore_limit = restore_limit
        self._retention = retention
        self._last_retention_result: AIAgentMemoryRetentionResult | None = None

    @property
    def last_retention_result(
        self,
    ) -> AIAgentMemoryRetentionResult | None:
        return self._last_retention_result

    async def persist(
        self,
        record: AIPlanMemoryRecord,
    ) -> int:
        record_id = await self._repository.add(
            record
        )

        if self._retention is not None:
            self._last_retention_result = await self._retention.enforce()

        return record_id

    async def restore(
        self,
    ) -> int:
        records = await self._repository.list_recent(
            limit=self._restore_limit
        )

        chronological = tuple(
            reversed(
                records
            )
        )

        self._store.load_records(
            chronological,
            replace=True,
        )

        return len(
            chronological
        )
