from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from jarvis.planner.ai_plan_adapter import (
    AIPlanAdaptationResult,
)
from jarvis.planner.ai_plan_contract import (
    AIPlanDraft,
    AIPlanStepDraft,
)
from jarvis.planner.ai_plan_execution import (
    AIPlanExecutionResult,
)
from jarvis.planner.ai_plan_memory import (
    AIPlanMemoryQuery,
    AIPlanMemoryStore,
)
from jarvis.planner.ai_plan_pipeline import (
    AIPlanPipelineResult,
)
from jarvis.planner.ai_plan_reflection import (
    AIPlanReflectionDecision,
    AIPlanReflectionResult,
)
from jarvis.planner.ai_plan_validation import (
    AIPlanValidationResult,
)
from jarvis.planner.executor import (
    PlanExecutionResult,
    PlanStepResult,
)
from jarvis.planner.models import (
    Plan,
    PlanStatus,
    PlanStep,
    PlanStepStatus,
)


def make_execution(
    *,
    goal: str,
    capability: str,
    success: bool,
) -> tuple[
    AIPlanExecutionResult,
    AIPlanReflectionResult,
]:
    step_status = (
        PlanStepStatus.COMPLETED
        if success
        else PlanStepStatus.FAILED
    )

    plan_status = (
        PlanStatus.COMPLETED
        if success
        else PlanStatus.FAILED
    )

    plan = Plan(
        goal=goal,
        steps=[
            PlanStep(
                index=1,
                capability=capability,
                arguments={},
                description=f"Execute {capability}",
                status=step_status,
            )
        ],
        status=plan_status,
    )

    validation = AIPlanValidationResult(
        valid=True,
        issues=(),
    )

    pipeline = AIPlanPipelineResult(
        draft=AIPlanDraft(
            goal=goal,
            steps=(
                AIPlanStepDraft(
                    capability=capability,
                ),
            ),
        ),
        adaptation=AIPlanAdaptationResult(
            plan=plan,
            validation=validation,
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
                    status=step_status,
                    error=(
                        None
                        if success
                        else "simulated failure"
                    ),
                )
            ],
        ),
    )

    reflection = AIPlanReflectionResult(
        decision=(
            AIPlanReflectionDecision.COMPLETE
            if success
            else AIPlanReflectionDecision.REVIEW
        ),
        success=success,
        completed_steps=(
            1
            if success
            else 0
        ),
        failed_steps=(
            0
            if success
            else 1
        ),
        findings=(),
    )

    return execution, reflection


def test_memory_remembers_and_queries_records() -> None:
    store = AIPlanMemoryStore()

    first_execution, first_reflection = make_execution(
        goal="Check health",
        capability="system.health",
        success=True,
    )

    second_execution, second_reflection = make_execution(
        goal="Ping Jarvis",
        capability="system.ping",
        success=False,
    )

    base = datetime(
        2026,
        8,
        4,
        10,
        0,
        tzinfo=UTC,
    )

    store.remember(
        execution=first_execution,
        reflection=first_reflection,
        created_at=base,
    )

    store.remember(
        execution=second_execution,
        reflection=second_reflection,
        created_at=base + timedelta(
            minutes=1
        ),
    )

    assert len(
        store
    ) == 2

    failed = store.query(
        AIPlanMemoryQuery(
            success=False
        )
    )

    assert len(
        failed
    ) == 1
    assert failed[0].goal == "Ping Jarvis"

    health = store.query(
        AIPlanMemoryQuery(
            capability="system.health"
        )
    )

    assert len(
        health
    ) == 1
    assert health[0].success is True


def test_memory_enforces_max_records() -> None:
    store = AIPlanMemoryStore(
        max_records=1
    )

    first_execution, first_reflection = make_execution(
        goal="First",
        capability="system.ping",
        success=True,
    )

    second_execution, second_reflection = make_execution(
        goal="Second",
        capability="system.health",
        success=True,
    )

    store.remember(
        execution=first_execution,
        reflection=first_reflection,
    )

    store.remember(
        execution=second_execution,
        reflection=second_reflection,
    )

    assert len(
        store
    ) == 1
    assert store.list_recent()[0].goal == "Second"


def test_memory_rejects_naive_timestamp() -> None:
    execution, reflection = make_execution(
        goal="Check",
        capability="system.ping",
        success=True,
    )

    with pytest.raises(
        ValueError,
        match="timezone-aware",
    ):
        AIPlanMemoryStore().remember(
            execution=execution,
            reflection=reflection,
            created_at=datetime(  # noqa: DTZ001
                2026,
                8,
                4,
                10,
                0,
            ),
        )
