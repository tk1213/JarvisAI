from __future__ import annotations

from jarvis.agent.memory_repository import AIAgentMemoryRepository
from jarvis.agent.memory_retention import (
    AIAgentMemoryRetentionPolicy,
    AIAgentMemoryRetentionResult,
)
from jarvis.core.logger import log
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

        self._last_retention_result: (
            AIAgentMemoryRetentionResult | None
        ) = None

        self._last_retention_error: str | None = None

    @property
    def last_retention_result(
        self,
    ) -> AIAgentMemoryRetentionResult | None:
        return self._last_retention_result

    @property
    def last_retention_error(
        self,
    ) -> str | None:
        return self._last_retention_error

    async def persist(
        self,
        record: AIPlanMemoryRecord,
    ) -> int:
        record_id = await self._repository.add(
            record
        )

        # The durable write has already succeeded.
        #
        # Retention is post-write maintenance. An ordinary
        # retention failure must not make the caller believe
        # that primary persistence failed.
        self._last_retention_result = None
        self._last_retention_error = None

        if self._retention is not None:
            try:
                self._last_retention_result = (
                    await self._retention.enforce()
                )

            except Exception as exc:  # noqa: BLE001
                self._last_retention_error = str(
                    exc
                )

                log.exception(
                    "Agent memory retention failed after durable "
                    "persistence; keeping the persisted record."
                )

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