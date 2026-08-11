from __future__ import annotations

from jarvis.agent.replanning import AIAgentReplanPolicy
from jarvis.planner.ai_plan_reflection import (
    AIPlanReflectionDecision,
    AIPlanReflectionFinding,
    AIPlanReflectionResult,
)


def main() -> None:
    policy = AIAgentReplanPolicy(
        max_replans=1,
        max_context_chars=600,
    )

    reflection = AIPlanReflectionResult(
        decision=AIPlanReflectionDecision.RETRY,
        success=False,
        completed_steps=0,
        failed_steps=1,
        findings=(
            AIPlanReflectionFinding(
                code="step_failed",
                message="Service temporarily unavailable.",
            ),
        ),
    )

    assert policy.should_replan(
        reflection=reflection,
        attempts=0,
    )
    assert not policy.should_replan(
        reflection=reflection,
        attempts=1,
    )

    retry_text = policy.build_retry_text(
        original_text="Check Jarvis",
        reflection=reflection,
        attempt=1,
    )

    assert "Agent retry context" in retry_text
    assert "read-only plan" in retry_text
    assert "side-effect action" in retry_text
    assert len(retry_text) <= 600

    print("Sprint 4.3 Pack C — Bounded Autonomous Replanning")
    print("-" * 60)
    print("Reflection retry decision: PASS")
    print("Maximum replan guard: PASS")
    print("Retry context boundary: PASS")
    print("Retry context budget: PASS")
    print("Sprint 4.3 Pack C live gate: PASS")


if __name__ == "__main__":
    main()
