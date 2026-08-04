from jarvis.planner.execution_health import (
    ExecutionHealthLevel,
    ExecutionHealthSnapshot,
)
from jarvis.planner.execution_health_report import (
    ExecutionHealthReportBuilder,
)


def test_health_report_formats_snapshot() -> None:
    snapshot = ExecutionHealthSnapshot(
        level=ExecutionHealthLevel.DEGRADED,
        total_executions=10,
        success_rate=0.8,
        retried_steps=3,
        timed_out_steps=1,
        unreliable_capabilities=(
            "system.health",
        ),
        reason="Execution reliability shows elevated retries.",
    )

    report = ExecutionHealthReportBuilder().build(
        snapshot
    )

    assert (
        "Execution health: degraded"
        in report.summary
    )
    assert (
        "success_rate=80.0%"
        in report.summary
    )
    assert (
        "Retried steps: 3"
        in report.lines
    )
    assert (
        "Timed out steps: 1"
        in report.lines
    )
    assert (
        "Unreliable capabilities: system.health"
        in report.lines
    )
