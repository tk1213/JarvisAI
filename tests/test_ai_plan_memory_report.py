from datetime import UTC, datetime

from jarvis.planner.ai_plan_memory import (
    AIPlanMemoryRecord,
)
from jarvis.planner.ai_plan_memory_report import (
    AIPlanMemoryReportBuilder,
)


def test_memory_report_formats_records() -> None:
    records = (
        AIPlanMemoryRecord(
            goal="Check health",
            capabilities=(
                "system.health",
            ),
            success=True,
            completed_steps=1,
            failed_steps=0,
            reflection_decision="complete",
            created_at=datetime(
                2026,
                8,
                4,
                10,
                0,
                tzinfo=UTC,
            ),
            metadata={},
        ),
    )

    report = AIPlanMemoryReportBuilder().build(
        records
    )

    assert (
        "1 record(s), 1 successful"
        in report.summary
    )
    assert (
        "goal='Check health'"
        in report.lines[0]
    )


def test_memory_report_handles_empty_records() -> None:
    report = AIPlanMemoryReportBuilder().build(
        ()
    )

    assert report.lines == (
        "No AI plan memory records are available.",
    )
