import pytest

from jarvis.planner.models import (
    Plan,
    PlanStatus,
    PlanStep,
    PlanStepStatus,
)


def test_plan_step_defaults() -> None:
    step = PlanStep(
        index=1,
        capability="system.ping",
    )

    assert step.status is PlanStepStatus.PENDING
    assert step.arguments == {}
    assert step.capability == "system.ping"


def test_plan_ready_shape() -> None:
    plan = Plan(
        goal="Check system",
        steps=[
            PlanStep(
                index=1,
                capability="system.ping",
            )
        ],
        status=PlanStatus.READY,
    )

    assert plan.goal == "Check system"
    assert plan.status is PlanStatus.READY
    assert len(plan.steps) == 1


def test_plan_rejects_empty_goal() -> None:
    with pytest.raises(
        ValueError,
        match="goal",
    ):
        Plan(
            goal=" ",
            steps=[
                PlanStep(
                    index=1,
                    capability="system.ping",
                )
            ],
        )


def test_plan_rejects_non_sequential_indexes() -> None:
    with pytest.raises(
        ValueError,
        match="sequential",
    ):
        Plan(
            goal="test",
            steps=[
                PlanStep(
                    index=2,
                    capability="system.ping",
                )
            ],
        )
