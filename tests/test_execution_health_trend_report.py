from jarvis.planner.execution_health import ExecutionHealthLevel
from jarvis.planner.execution_health_trend_report import (
    ExecutionHealthTrendReportBuilder,
)
from jarvis.planner.execution_health_trends import (
    ExecutionHealthTrend,
    ExecutionHealthWindow,
)


def test_trend_report_formats_windows() -> None:
    trend = ExecutionHealthTrend(
        current=ExecutionHealthWindow(
            size=10,
            completed=8,
            failed=2,
            retries=3,
            timeouts=1,
        ),
        previous=ExecutionHealthWindow(
            size=10,
            completed=9,
            failed=1,
            retries=1,
            timeouts=0,
        ),
        direction="worsening",
        level=ExecutionHealthLevel.DEGRADED,
        reason="Current execution window shows degraded reliability.",
    )

    report = ExecutionHealthTrendReportBuilder().build(
        trend
    )

    assert (
        "Execution health trend: worsening"
        in report.summary
    )
    assert (
        "current_success_rate=80.0%"
        in report.summary
    )
    assert (
        "Current window: size=10"
        in report.lines[0]
    )
    assert (
        "Previous window: size=10"
        in report.lines[1]
    )
