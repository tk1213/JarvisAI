from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from jarvis.planner.ai_plan_execution import (
    AIPlanExecutionResult,
)
from jarvis.planner.models import PlanStepStatus


class AIPlanReflectionDecision(StrEnum):
    COMPLETE = "complete"
    RETRY = "retry"
    REVIEW = "review"


@dataclass(slots=True, frozen=True)
class AIPlanReflectionFinding:
    code: str
    message: str
    step_index: int | None = None
    capability: str | None = None


@dataclass(slots=True, frozen=True)
class AIPlanReflectionResult:
    decision: AIPlanReflectionDecision
    success: bool
    completed_steps: int
    failed_steps: int
    findings: tuple[
        AIPlanReflectionFinding,
        ...
    ]


class AIPlanReflectionService:
    def reflect(
        self,
        result: AIPlanExecutionResult,
    ) -> AIPlanReflectionResult:
        findings: list[
            AIPlanReflectionFinding
        ] = []

        failed_steps = 0
        retryable_failures = 0

        for step_result in result.execution.step_results:
            if step_result.status is PlanStepStatus.COMPLETED:
                continue

            failed_steps += 1

            error = (
                step_result.error
                or "Unknown execution failure."
            )

            findings.append(
                AIPlanReflectionFinding(
                    code="step_failed",
                    message=error,
                    step_index=step_result.step_index,
                    capability=step_result.capability,
                )
            )

            normalized_error = error.casefold()

            if (
                "timed out" in normalized_error
                or "temporar" in normalized_error
                or "unavailable" in normalized_error
            ):
                retryable_failures += 1

        if result.success:
            decision = AIPlanReflectionDecision.COMPLETE

            findings.append(
                AIPlanReflectionFinding(
                    code="plan_completed",
                    message=(
                        "The AI-generated plan completed "
                        "successfully."
                    ),
                )
            )

        elif (
            failed_steps > 0
            and retryable_failures == failed_steps
        ):
            decision = AIPlanReflectionDecision.RETRY

            findings.append(
                AIPlanReflectionFinding(
                    code="retry_recommended",
                    message=(
                        "All observed failures appear transient "
                        "and may be retried."
                    ),
                )
            )

        else:
            decision = AIPlanReflectionDecision.REVIEW

            findings.append(
                AIPlanReflectionFinding(
                    code="manual_review_recommended",
                    message=(
                        "The execution should be reviewed before "
                        "another attempt."
                    ),
                )
            )

        return AIPlanReflectionResult(
            decision=decision,
            success=result.success,
            completed_steps=result.completed_steps,
            failed_steps=failed_steps,
            findings=tuple(
                findings
            ),
        )
