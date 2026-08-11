from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from jarvis.agent.memory import AIAgentMemoryLifecycle
from jarvis.agent.runtime import AIAgentRuntime
from jarvis.planner.ai_plan_memory import AIPlanMemoryStore


@dataclass(slots=True, frozen=True)
class AIAgentSessionSnapshot:
    has_pending_plan: bool
    memory_records: int
    latest_goal: str | None
    latest_success: bool | None
    created_at: datetime
    latest_memory_source: str | None = None
    last_run_status: str | None = None
    last_replan_attempts: int = 0


class AIAgentSessionService:
    def __init__(
        self,
        *,
        runtime: AIAgentRuntime,
        memory: AIPlanMemoryStore,
        memory_lifecycle: AIAgentMemoryLifecycle | None = None,
    ) -> None:
        self._runtime = runtime
        self._memory = memory
        self._memory_lifecycle = (
            memory_lifecycle
            if memory_lifecycle is not None
            else runtime.memory_lifecycle
        )

    def snapshot(
        self,
        *,
        created_at: datetime | None = None,
    ) -> AIAgentSessionSnapshot:
        timestamp = (
            created_at
            if created_at is not None
            else datetime.now(UTC)
        )

        if timestamp.tzinfo is None:
            raise ValueError(
                "created_at must be timezone-aware."
            )

        memory_snapshot = self._memory_lifecycle.snapshot(
            created_at=timestamp
        )

        last_result = self._runtime.last_result

        return AIAgentSessionSnapshot(
            has_pending_plan=self._runtime.has_pending_plan,
            memory_records=memory_snapshot.records,
            latest_goal=memory_snapshot.latest_goal,
            latest_success=memory_snapshot.latest_success,
            created_at=timestamp,
            latest_memory_source=memory_snapshot.latest_source,
            last_run_status=(
                last_result.status.value
                if last_result is not None
                else None
            ),
            last_replan_attempts=(
                last_result.replan_attempts
                if last_result is not None
                else 0
            ),
        )
