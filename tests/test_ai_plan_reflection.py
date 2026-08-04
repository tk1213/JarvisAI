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
from jarvis.planner.ai_plan_pipeline import (
    AIPlanPipelineResult,
)
from jarvis.planner.ai_plan_reflection import (
    AIPlanReflectionDecision,
    AIPlanReflectionService,
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


def make_result(
    *,
    status: PlanStatus,
    step_status: PlanStepStatus,
    error: str | None = None,
) -> AIPlanExecutionResult:
    plan = Plan(
        goal="Check Jarvis",
        steps=[
            PlanStep(
                index=1,
                capability="system.ping",
                arguments={},
                description="Execute system.ping",
                status=step_status,
            )
        ],
        status=status,
    )

    validation = AIPlanValidationResult(
        valid=True,
        issues=(),
    )

    pipeline = AIPlanPipelineResult(
        draft=AIPlanDraft(
            goal="Check Jarvis",
            steps=(
                AIPlanStepDraft(
                    capability="system.ping",
                ),
            ),
        ),
        adaptation=AIPlanAdaptationResult(
            plan=plan,
            validation=validation,
        ),
    )

    execution = PlanExecutionResult(
        plan=plan,
        step_results=[
            PlanStepResult(
                step_index=1,
                capability="system.ping",
                status=step_status,
                error=error,
            )
        ],
    )

    return AIPlanExecutionResult(
        pipeline=pipeline,
        execution=execution,
    )


def test_reflection_completes_successful_plan() -> None:
    result = AIPlanReflectionService().reflect(
        make_result(
            status=PlanStatus.COMPLETED,
            step_status=PlanStepStatus.COMPLETED,
        )
    )

    assert (
        result.decision
        is AIPlanReflectionDecision.COMPLETE
    )
    assert result.success is True
    assert result.failed_steps == 0


def test_reflection_recommends_retry_for_timeout() -> None:
    result = AIPlanReflectionService().reflect(
        make_result(
            status=PlanStatus.FAILED,
            step_status=PlanStepStatus.FAILED,
            error="capability execution timed out",
        )
    )

    assert (
        result.decision
        is AIPlanReflectionDecision.RETRY
    )
    assert result.failed_steps == 1


def test_reflection_recommends_review_for_non_transient_error() -> None:
    result = AIPlanReflectionService().reflect(
        make_result(
            status=PlanStatus.FAILED,
            step_status=PlanStepStatus.FAILED,
            error="permission denied",
        )
    )

    assert (
        result.decision
        is AIPlanReflectionDecision.REVIEW
    )
