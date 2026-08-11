from __future__ import annotations

import pytest

from jarvis.wake.activation import (
    WakeActivationPolicy,
    WakeActivationStatus,
)


def test_score_at_threshold_detects() -> None:
    policy = WakeActivationPolicy(
        threshold=0.50,
    )

    result = policy.evaluate(
        0.50
    )

    assert result.detected is True
    assert result.status is WakeActivationStatus.DETECTED
    assert result.score == pytest.approx(
        0.50
    )


def test_score_below_threshold_is_not_detected() -> None:
    policy = WakeActivationPolicy(
        threshold=0.50,
    )

    result = policy.evaluate(
        0.49
    )

    assert result.detected is False
    assert result.status is WakeActivationStatus.CANCELLED


@pytest.mark.parametrize(
    "threshold",
    (
        0.0,
        -0.1,
        1.1,
    ),
)
def test_invalid_threshold_is_rejected(
    threshold: float,
) -> None:
    with pytest.raises(
        ValueError,
        match="threshold",
    ):
        WakeActivationPolicy(
            threshold=threshold,
        )


@pytest.mark.parametrize(
    "score",
    (
        -0.1,
        1.1,
    ),
)
def test_invalid_score_is_rejected(
    score: float,
) -> None:
    policy = WakeActivationPolicy(
        threshold=0.5,
    )

    with pytest.raises(
        ValueError,
        match="score",
    ):
        policy.evaluate(
            score
        )
