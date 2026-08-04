from jarvis.planner.capability_reliability import (
    CapabilityReliability,
    CapabilityReliabilitySummary,
)
from jarvis.planner.capability_reliability_report import (
    CapabilityReliabilityReportBuilder,
)


def test_report_formats_reliability_metrics() -> None:
    summary = CapabilityReliabilitySummary(
        total_capabilities=1,
        capabilities=(
            CapabilityReliability(
                capability="system.ping",
                executions=4,
                failures=1,
                retries=2,
                timeouts=1,
            ),
        ),
    )

    report = CapabilityReliabilityReportBuilder().build(
        summary
    )

    assert (
        report.summary
        == "Capability reliability: 1 capability record(s)."
    )

    assert report.lines == (
        (
            "system.ping: executions=4, failures=1, "
            "retries=2, timeouts=1, success_rate=75.0%"
        ),
    )
