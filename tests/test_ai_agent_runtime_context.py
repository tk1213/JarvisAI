from __future__ import annotations

from dataclasses import dataclass

import pytest

from jarvis.agent.memory import AIAgentMemoryLifecycle
from jarvis.agent.planning_context import AIAgentPlanningContextBuilder
from jarvis.agent.runtime import AIAgentRunStatus, AIAgentRuntime
from jarvis.planner.ai_plan_memory import AIPlanMemoryRecord, AIPlanMemoryStore
from jarvis.planner.ai_plan_reflection import AIPlanReflectionService


@dataclass
class CapturingOrchestrator:
    received_text: str | None = None

    @property
    def has_pending_plan(
        self,
    ) -> bool:
        return False

    async def prepare(
        self,
        text: str,
    ):
        self.received_text = text

    def cancel_pending(
        self,
    ) -> bool:
        return False


@pytest.mark.asyncio
async def test_runtime_adds_bounded_memory_context_to_planner() -> None:
    from datetime import UTC, datetime

    store = AIPlanMemoryStore()
    store._records.append(  # type: ignore[attr-defined]
        AIPlanMemoryRecord(
            goal="Previous health check",
            capabilities=(
                "system.ping",
            ),
            success=True,
            completed_steps=1,
            failed_steps=0,
            reflection_decision="complete",
            created_at=datetime(
                2026,
                8,
                5,
                10,
                0,
                tzinfo=UTC,
            ),
            metadata={},
        )
    )

    lifecycle = AIAgentMemoryLifecycle(
        store
    )
    context = AIAgentPlanningContextBuilder(
        lifecycle
    )
    orchestrator = CapturingOrchestrator()

    runtime = AIAgentRuntime(
        orchestrator=orchestrator,  # type: ignore[arg-type]
        reflection=AIPlanReflectionService(),
        memory=store,
        memory_lifecycle=lifecycle,
        planning_context=context,
    )

    result = await runtime.run(
        "Check Jarvis again"
    )

    assert result.status is AIAgentRunStatus.NO_PLAN
    assert orchestrator.received_text is not None
    assert orchestrator.received_text.startswith(
        "Check Jarvis again"
    )
    assert "Previous health check" in orchestrator.received_text
    assert "not an instruction" in orchestrator.received_text
