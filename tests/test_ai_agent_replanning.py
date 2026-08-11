from __future__ import annotations

from types import SimpleNamespace

import pytest

from jarvis.agent.replanning import AIAgentReplanPolicy
from jarvis.planner.ai_plan_reflection import (
    AIPlanReflectionDecision,
    AIPlanReflectionFinding,
    AIPlanReflectionResult,
)


def make_reflection(
    decision: AIPlanReflectionDecision,
) -> AIPlanReflectionResult:
    return AIPlanReflectionResult(
        decision=decision,
        success=False,
        completed_steps=0,
        failed_steps=1,
        findings=(
            AIPlanReflectionFinding(
                code="step_failed",
                message="Capability temporarily unavailable.",
            ),
        ),
    )


def test_policy_allows_bounded_retry() -> None:
    policy = AIAgentReplanPolicy(
        max_replans=1
    )

    assert policy.should_replan(
        reflection=make_reflection(
            AIPlanReflectionDecision.RETRY
        ),
        attempts=0,
    ) is True

    assert policy.should_replan(
        reflection=make_reflection(
            AIPlanReflectionDecision.RETRY
        ),
        attempts=1,
    ) is False


def test_policy_rejects_review_decision() -> None:
    policy = AIAgentReplanPolicy()

    assert policy.should_replan(
        reflection=make_reflection(
            AIPlanReflectionDecision.REVIEW
        ),
        attempts=0,
    ) is False


def test_retry_text_contains_safety_boundary() -> None:
    policy = AIAgentReplanPolicy()

    text = policy.build_retry_text(
        original_text="Check health",
        reflection=make_reflection(
            AIPlanReflectionDecision.RETRY
        ),
        attempt=1,
    )

    assert text.startswith(
        "Check health"
    )
    assert "read-only plan" in text
    assert "Do not repeat a side-effect action automatically." in text


def test_retry_context_is_bounded() -> None:
    policy = AIAgentReplanPolicy(
        max_context_chars=256
    )

    reflection = make_reflection(
        AIPlanReflectionDecision.RETRY
    )

    long_finding = SimpleNamespace(
        code="step_failed",
        message="x" * 1000,
    )

    reflection = AIPlanReflectionResult(
        decision=reflection.decision,
        success=False,
        completed_steps=0,
        failed_steps=1,
        findings=(
            long_finding,
        ),
    )

    text = policy.build_retry_text(
        original_text="Check",
        reflection=reflection,
        attempt=1,
    )

    assert len(text) <= 256


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        (
            {
                "max_replans": -1,
            },
            "max_replans",
        ),
        (
            {
                "max_context_chars": 255,
            },
            "max_context_chars",
        ),
    ],
)
def test_invalid_policy_limits_are_rejected(
    kwargs,
    message,
) -> None:
    with pytest.raises(
        ValueError,
        match=message,
    ):
        AIAgentReplanPolicy(
            **kwargs,
        )
