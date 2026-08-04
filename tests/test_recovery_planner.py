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
from jarvis.planner.recovery import RecoveryPlanner


def test_recovery_flags_completed_side_effect_for_review() -> None:
    plan = Plan(
        goal="Change then fail",
        steps=[
            PlanStep(
                index=1,
                capability="smart_home.turn_on",
                status=PlanStepStatus.COMPLETED,
            ),
            PlanStep(
                index=2,
                capability="system.ping",
                status=PlanStepStatus.FAILED,
            ),
        ],
        status=PlanStatus.FAILED,
    )

    execution = PlanExecutionResult(
        plan=plan,
        step_results=[
            PlanStepResult(
                step_index=1,
                capability="smart_home.turn_on",
                status=PlanStepStatus.COMPLETED,
            ),
            PlanStepResult(
                step_index=2,
                capability="system.ping",
                status=PlanStepStatus.FAILED,
                error="failure",
            ),
        ],
    )

    assessment = RecoveryPlanner().assess(
        execution
    )

    assert (
        assessment.requires_compensation_review
        is True
    )
    assert len(
        assessment.compensation.candidates
    ) == 1
