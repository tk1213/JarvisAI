from __future__ import annotations

import asyncio

from jarvis.agent.memory import AIAgentMemoryLifecycle
from jarvis.agent.memory_retention import (
    AIAgentMemoryRetentionPolicy,
    AIAgentMemoryRetentionResult,
)


class AIAgentMemoryStartupService:
    """Restores durable agent memory after the database is ready."""

    def __init__(
        self,
        lifecycle: AIAgentMemoryLifecycle,
        *,
        retention: AIAgentMemoryRetentionPolicy | None = None,
    ) -> None:
        self._lifecycle = lifecycle
        self._retention = retention
        self._retention_result: AIAgentMemoryRetentionResult | None = None
        self._restored = False
        self._restored_records = 0
        self._restore_lock = asyncio.Lock()

    @property
    def retention_result(self) -> AIAgentMemoryRetentionResult | None:
        return self._retention_result

    @property
    def restored(self) -> bool:
        return self._restored

    @property
    def restored_records(self) -> int:
        return self._restored_records

    async def restore(
        self,
    ) -> int:
        if self._restored:
            return self._restored_records

        async with self._restore_lock:
            if self._restored:
                return self._restored_records

            if self._retention is not None:
                self._retention_result = (
                    await self._retention.enforce()
                )

            restored = (
                await self._lifecycle.restore_durable_memory()
            )

            self._restored = True
            self._restored_records = restored

            return restored