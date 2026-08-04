from jarvis.planner.compensation import (
    CompensationCandidate,
    CompensationPlan,
    CompensationStatus,
)
from jarvis.planner.executor import PlanExecutionResult
from jarvis.planner.models import (
    Plan,
    PlanStatus,
    PlanStep,
    PlanStepStatus,
)
from jarvis.planner.recovery import RecoveryAssessment
from jarvis.planner.recovery_policy import (
    RecoveryDecision,
    RecoveryDecisionType,
)
from jarvis.planner.recovery_report import RecoveryReportBuilder


def test_report_lists_manual_review_candidates() -> None:
    plan = Plan(
        goal="Change then fail",
        steps=[
            PlanStep(
                index=1,
                capability="smart_home.turn_off",
                status=PlanStepStatus.COMPLETED,
            ),
        ],
        status=PlanStatus.FAILED,
    )

    execution = PlanExecutionResult(
        plan=plan,
        step_results=[],
    )

    candidate = CompensationCandidate(
        step_index=1,
        capability="smart_home.turn_off",
        arguments={
            "device_query": "Smart Plug 1",
        },
    )

    assessment = RecoveryAssessment(
        execution=execution,
        compensation=CompensationPlan(
            status=CompensationStatus.REQUIRES_REVIEW,
            candidates=(candidate,),
            reason="Review required.",
        ),
        decision=RecoveryDecision(
            decision=RecoveryDecisionType.MANUAL_REVIEW,
            candidates=(candidate,),
            reason="Manual review.",
        ),
    )

    report = RecoveryReportBuilder().build(
        assessment
    )

    assert (
        report.summary
        == (
            "Manual compensation review is required "
            "before any recovery action."
        )
    )
    assert (
        "smart_home.turn_off"
        in report.details[0]
    )
