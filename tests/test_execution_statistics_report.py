from jarvis.planner.execution_statistics import (
    ExecutionStatistics,
)
from jarvis.planner.execution_statistics_report import (
    ExecutionStatisticsReportBuilder,
)


def test_statistics_report_formats_summary_and_capabilities() -> None:
    statistics = ExecutionStatistics(
        total=4,
        completed=3,
        failed=1,
        retried_steps=2,
        timed_out_steps=1,
        capability_counts={
            "system.health": 2,
            "system.ping": 2,
        },
        capability_failure_counts={
            "system.health": 1,
        },
    )

    report = ExecutionStatisticsReportBuilder().build(
        statistics
    )

    assert (
        "4 record(s), 3 completed, 1 failed"
        in report.summary
    )
    assert (
        "success_rate=75.0%"
        in report.summary
    )
    assert (
        "Retried steps: 2"
        in report.lines
    )
    assert (
        "Timed out steps: 1"
        in report.lines
    )
    assert (
        "system.health: steps=2, failures=1"
        in report.lines
    )
