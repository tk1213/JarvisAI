import pytest

from jarvis.planner.deadline import PlanDeadlinePolicy


def test_default_deadline_is_positive() -> None:
    policy = PlanDeadlinePolicy()

    assert policy.plan_timeout_seconds > 0


def test_invalid_deadline_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="greater than 0",
    ):
        PlanDeadlinePolicy(
            plan_timeout_seconds=0
        )
