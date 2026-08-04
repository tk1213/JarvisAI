import pytest

from jarvis.planner.retry import (
    RetryDecision,
    RetryPolicy,
)


def test_retry_policy_retries_before_max_attempts() -> None:
    policy = RetryPolicy(
        max_attempts=3
    )

    assert (
        policy.decide(
            attempt=1
        )
        is RetryDecision.RETRY
    )

    assert (
        policy.decide(
            attempt=2
        )
        is RetryDecision.RETRY
    )


def test_retry_policy_fails_at_max_attempts() -> None:
    policy = RetryPolicy(
        max_attempts=3
    )

    assert (
        policy.decide(
            attempt=3
        )
        is RetryDecision.FAIL
    )


def test_read_only_capability_can_retry() -> None:
    policy = RetryPolicy(
        max_attempts=2
    )

    assert (
        policy.decide_for_capability(
            capability="system.ping",
            attempt=1,
        )
        is RetryDecision.RETRY
    )


def test_side_effect_capability_does_not_retry() -> None:
    policy = RetryPolicy(
        max_attempts=3
    )

    assert (
        policy.decide_for_capability(
            capability="smart_home.turn_off",
            attempt=1,
        )
        is RetryDecision.FAIL
    )


def test_toggle_does_not_retry() -> None:
    policy = RetryPolicy(
        max_attempts=3
    )

    assert (
        policy.decide_for_capability(
            capability="smart_home.toggle",
            attempt=1,
        )
        is RetryDecision.FAIL
    )


def test_unknown_capability_does_not_retry() -> None:
    policy = RetryPolicy(
        max_attempts=3
    )

    assert (
        policy.decide_for_capability(
            capability="future.device.calibrate",
            attempt=1,
        )
        is RetryDecision.FAIL
    )


def test_retry_policy_rejects_invalid_max_attempts() -> None:
    with pytest.raises(
        ValueError,
        match="at least 1",
    ):
        RetryPolicy(
            max_attempts=0
        )


def test_retry_policy_rejects_invalid_attempt() -> None:
    policy = RetryPolicy()

    with pytest.raises(
        ValueError,
        match="at least 1",
    ):
        policy.decide(
            attempt=0
        )
