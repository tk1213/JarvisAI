from jarvis.planner.compensation import (
    CompensationCandidate,
    CompensationPlan,
    CompensationStatus,
)
from jarvis.planner.recovery_policy import (
    RecoveryDecisionType,
    RecoveryPolicy,
)


def test_no_compensation_returns_none_decision() -> None:
    plan = CompensationPlan(
        status=CompensationStatus.NOT_REQUIRED,
        reason="Nothing to compensate.",
    )

    decision = RecoveryPolicy().decide(
        plan
    )

    assert (
        decision.decision
        is RecoveryDecisionType.NONE
    )
    assert decision.requires_manual_review is False


def test_compensation_candidates_require_manual_review() -> None:
    plan = CompensationPlan(
        status=CompensationStatus.REQUIRES_REVIEW,
        candidates=(
            CompensationCandidate(
                step_index=1,
                capability="smart_home.turn_off",
                arguments={
                    "device_query": "Smart Plug 1",
                },
            ),
        ),
        reason="Review required.",
    )

    decision = RecoveryPolicy().decide(
        plan
    )

    assert (
        decision.decision
        is RecoveryDecisionType.MANUAL_REVIEW
    )
    assert decision.requires_manual_review is True
    assert len(
        decision.candidates
    ) == 1
