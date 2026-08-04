from __future__ import annotations

from dataclasses import dataclass

from jarvis.planner.recovery import RecoveryAssessment


@dataclass(slots=True, frozen=True)
class RecoveryReport:
    summary: str
    details: tuple[str, ...]


class RecoveryReportBuilder:
    def build(
        self,
        assessment: RecoveryAssessment,
    ) -> RecoveryReport:
        execution = assessment.execution

        if not assessment.requires_compensation_review:
            return RecoveryReport(
                summary=(
                    "No compensation review is required."
                ),
                details=(
                    f"Plan status: {execution.plan.status.value}",
                ),
            )

        details = tuple(
            (
                f"Step {candidate.step_index}: "
                f"{candidate.capability} "
                f"{candidate.arguments}"
            )
            for candidate
            in assessment.decision.candidates
        )

        return RecoveryReport(
            summary=(
                "Manual compensation review is required "
                "before any recovery action."
            ),
            details=details,
        )
