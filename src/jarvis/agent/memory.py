from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from jarvis.agent.memory_persistence import AIAgentMemoryPersistence
from jarvis.planner.ai_plan_execution import AIPlanExecutionResult
from jarvis.planner.ai_plan_memory import (
    AIPlanMemoryRecord,
    AIPlanMemoryStore,
)
from jarvis.planner.ai_plan_reflection import AIPlanReflectionResult


@dataclass(slots=True, frozen=True)
class AIAgentMemorySnapshot:
    records: int
    latest_goal: str | None
    latest_success: bool | None
    latest_source: str | None
    created_at: datetime


class AIAgentMemoryLifecycle:
    """Owns the agent-facing lifecycle of AI plan execution memory."""

    def __init__(
        self,
        store: AIPlanMemoryStore,
        *,
        persistence: AIAgentMemoryPersistence | None = None,
    ) -> None:
        self._store = store
        self._persistence = persistence

    @property
    def store(self) -> AIPlanMemoryStore:
        return self._store

    def remember_execution(
        self,
        *,
        execution: AIPlanExecutionResult,
        reflection: AIPlanReflectionResult,
        source: str,
        created_at: datetime | None = None,
    ) -> AIPlanMemoryRecord:
        normalized_source = source.strip()

        if not normalized_source:
            raise ValueError(
                "memory source cannot be empty."
            )

        return self._store.remember(
            execution=execution,
            reflection=reflection,
            metadata={
                "source": normalized_source,
            },
            created_at=created_at,
        )

    async def remember_execution_durable(
        self,
        *,
        execution: AIPlanExecutionResult,
        reflection: AIPlanReflectionResult,
        source: str,
        created_at: datetime | None = None,
    ) -> AIPlanMemoryRecord:
        record = self.remember_execution(
            execution=execution,
            reflection=reflection,
            source=source,
            created_at=created_at,
        )

        if self._persistence is not None:
            await self._persistence.persist(
                record
            )

        return record

    async def restore_durable_memory(
        self,
    ) -> int:
        if self._persistence is None:
            return 0

        return await self._persistence.restore()

    def list_recent(
        self,
        *,
        limit: int = 20,
    ) -> tuple[AIPlanMemoryRecord, ...]:
        return self._store.list_recent(
            limit=limit
        )

    def snapshot(
        self,
        *,
        created_at: datetime | None = None,
    ) -> AIAgentMemorySnapshot:
        timestamp = (
            created_at
            if created_at is not None
            else datetime.now(UTC)
        )

        if timestamp.tzinfo is None:
            raise ValueError(
                "created_at must be timezone-aware."
            )

        recent = self.list_recent(
            limit=1
        )

        latest = (
            recent[0]
            if recent
            else None
        )

        source = None

        if latest is not None:
            raw_source = latest.metadata.get(
                "source"
            )

            if raw_source is not None:
                source = str(
                    raw_source
                )

        return AIAgentMemorySnapshot(
            records=len(
                self._store
            ),
            latest_goal=(
                latest.goal
                if latest is not None
                else None
            ),
            latest_success=(
                latest.success
                if latest is not None
                else None
            ),
            latest_source=source,
            created_at=timestamp,
        )

    def clear(
        self,
    ) -> None:
        self._store.clear()
