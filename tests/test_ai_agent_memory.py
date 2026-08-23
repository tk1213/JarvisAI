from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock, Mock

import pytest

from jarvis.agent.memory import AIAgentMemoryLifecycle
from jarvis.planner.ai_plan_adapter import AIPlanAdaptationResult
from jarvis.planner.ai_plan_contract import AIPlanDraft, AIPlanStepDraft
from jarvis.planner.ai_plan_execution import AIPlanExecutionResult
from jarvis.planner.ai_plan_memory import (
    AIPlanMemoryRecord,
    AIPlanMemoryStore,
)
from jarvis.planner.ai_plan_pipeline import AIPlanPipelineResult
from jarvis.planner.ai_plan_reflection import (
    AIPlanReflectionDecision,
    AIPlanReflectionResult,
)
from jarvis.planner.ai_plan_validation import AIPlanValidationResult
from jarvis.planner.executor import PlanExecutionResult, PlanStepResult
from jarvis.planner.models import (
    Plan,
    PlanStatus,
    PlanStep,
    PlanStepStatus,
)


def make_record(
    *,
    source: str = "test",
) -> AIPlanMemoryRecord:
    return AIPlanMemoryRecord(
        goal="Check Jarvis",
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
        metadata={
            "source": source,
        },
    )

def make_execution() -> tuple[
    AIPlanExecutionResult,
    AIPlanReflectionResult,
]:
    capability = "system.ping"

    plan = Plan(
        goal="Check Jarvis",
        steps=[
            PlanStep(
                index=1,
                capability=capability,
                arguments={},
                description=f"Execute {capability}",
                status=PlanStepStatus.COMPLETED,
            )
        ],
        status=PlanStatus.COMPLETED,
    )

    pipeline = AIPlanPipelineResult(
        draft=AIPlanDraft(
            goal="Check Jarvis",
            steps=(
                AIPlanStepDraft(
                    capability=capability,
                ),
            ),
        ),
        adaptation=AIPlanAdaptationResult(
            plan=plan,
            validation=AIPlanValidationResult(
                valid=True,
                issues=(),
            ),
        ),
    )

    execution = AIPlanExecutionResult(
        pipeline=pipeline,
        execution=PlanExecutionResult(
            plan=plan,
            step_results=[
                PlanStepResult(
                    step_index=1,
                    capability=capability,
                    status=PlanStepStatus.COMPLETED,
                    error=None,
                )
            ],
        ),
    )

    reflection = AIPlanReflectionResult(
        decision=AIPlanReflectionDecision.COMPLETE,
        success=True,
        completed_steps=1,
        failed_steps=0,
        findings=(),
    )

    return execution, reflection

def test_snapshot_reports_latest_record() -> None:
    store = AIPlanMemoryStore()
    store._records.append(  # type: ignore[attr-defined]
        make_record(
            source="ai_agent_runtime"
        )
    )

    snapshot = AIAgentMemoryLifecycle(
        store
    ).snapshot(
        created_at=datetime(
            2026,
            8,
            5,
            11,
            0,
            tzinfo=UTC,
        )
    )

    assert snapshot.records == 1
    assert snapshot.latest_goal == "Check Jarvis"
    assert snapshot.latest_success is True
    assert snapshot.latest_source == "ai_agent_runtime"


def test_snapshot_handles_empty_store() -> None:
    snapshot = AIAgentMemoryLifecycle(
        AIPlanMemoryStore()
    ).snapshot()

    assert snapshot.records == 0
    assert snapshot.latest_goal is None
    assert snapshot.latest_success is None
    assert snapshot.latest_source is None


def test_snapshot_rejects_naive_timestamp() -> None:
    with pytest.raises(
        ValueError,
        match="timezone-aware",
    ):
        AIAgentMemoryLifecycle(
            AIPlanMemoryStore()
        ).snapshot(
            created_at=datetime(  # noqa: DTZ001
                2026,
                8,
                5,
                10,
                0,
            )
        )


def test_clear_delegates_to_store() -> None:
    store = AIPlanMemoryStore()
    store._records.append(  # type: ignore[attr-defined]
        make_record()
    )

    lifecycle = AIAgentMemoryLifecycle(
        store
    )

    lifecycle.clear()

    assert len(store) == 0


def test_remember_execution_rejects_empty_source() -> None:
    lifecycle = AIAgentMemoryLifecycle(
        AIPlanMemoryStore()
    )

    with pytest.raises(
        ValueError,
        match="source",
    ):
        lifecycle.remember_execution(
            execution=Mock(),
            reflection=Mock(),
            source=" ",
        )


@pytest.mark.asyncio
async def test_durable_memory_keeps_in_memory_record_when_primary_persistence_fails() -> None:
    store = AIPlanMemoryStore()

    persistence = Mock()
    persistence.persist = AsyncMock(
        side_effect=RuntimeError(
            "persistence failed"
        )
    )

    lifecycle = AIAgentMemoryLifecycle(
        store,
        persistence=persistence,
    )

    execution, reflection = make_execution()

    with pytest.raises(
        RuntimeError,
        match="persistence failed",
    ):
        await lifecycle.remember_execution_durable(
            execution=execution,
            reflection=reflection,
            source="ai_agent_runtime",
        )

    assert len(store) == 1

    recent = store.list_recent(
        limit=1
    )

    assert len(recent) == 1
    assert recent[0].goal == "Check Jarvis"
    assert recent[0].metadata["source"] == "ai_agent_runtime"

    persistence.persist.assert_awaited_once_with(
        recent[0]
    )