import pytest

from jarvis.planner.timeout import ExecutionTimeoutPolicy


def test_default_timeout_is_positive() -> None:
    policy = ExecutionTimeoutPolicy()

    assert policy.step_timeout_seconds > 0


def test_invalid_timeout_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="greater than 0",
    ):
        ExecutionTimeoutPolicy(
            step_timeout_seconds=0
        )
