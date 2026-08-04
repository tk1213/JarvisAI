from jarvis.planner.ai_plan_reflection import (
    AIPlanReflectionDecision,
    AIPlanReflectionFinding,
    AIPlanReflectionResult,
)
from jarvis.planner.ai_plan_reflection_report import (
    AIPlanReflectionReportBuilder,
)


def test_reflection_report_formats_findings() -> None:
    reflection = AIPlanReflectionResult(
        decision=AIPlanReflectionDecision.RETRY,
        success=False,
        completed_steps=1,
        failed_steps=1,
        findings=(
            AIPlanReflectionFinding(
                code="step_failed",
                message="capability execution timed out",
                step_index=2,
                capability="system.health",
            ),
        ),
    )

    report = AIPlanReflectionReportBuilder().build(
        reflection
    )

    assert (
        "decision=retry"
        in report.summary
    )
    assert (
        "completed_steps=1"
        in report.summary
    )
    assert (
        report.lines[0]
        == (
            "step_failed: step=2 capability=system.health "
            "capability execution timed out"
        )
    )
