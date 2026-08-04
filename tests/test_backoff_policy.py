import pytest

from jarvis.planner.backoff import BackoffPolicy


def test_backoff_grows_exponentially() -> None:
    policy = BackoffPolicy(
        base_delay_seconds=0.5,
        multiplier=2.0,
        max_delay_seconds=10.0,
    )

    assert policy.delay_for_retry(
        attempt=1
    ) == 0.5

    assert policy.delay_for_retry(
        attempt=2
    ) == 1.0

    assert policy.delay_for_retry(
        attempt=3
    ) == 2.0


def test_backoff_is_capped() -> None:
    policy = BackoffPolicy(
        base_delay_seconds=1.0,
        multiplier=3.0,
        max_delay_seconds=2.0,
    )

    assert policy.delay_for_retry(
        attempt=3
    ) == 2.0


def test_invalid_attempt_is_rejected() -> None:
    policy = BackoffPolicy()

    with pytest.raises(
        ValueError,
        match="at least 1",
    ):
        policy.delay_for_retry(
            attempt=0
        )
