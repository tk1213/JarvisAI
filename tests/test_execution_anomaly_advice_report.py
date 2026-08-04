from jarvis.planner.execution_anomaly_advice import (
    ExecutionAnomalyAdvice,
    ExecutionAnomalyAdviceSummary,
)
from jarvis.planner.execution_anomaly_advice_report import (
    ExecutionAnomalyAdviceReportBuilder,
)


def test_advice_report_formats_recommendations() -> None:
    advice = ExecutionAnomalyAdviceSummary(
        total=1,
        advice=(
            ExecutionAnomalyAdvice(
                priority=1,
                anomaly_code="unreliable_capability",
                capability="system.health",
                recommendation="Inspect dependencies.",
            ),
        ),
    )

    report = ExecutionAnomalyAdviceReportBuilder().build(
        advice
    )

    assert (
        report.summary
        == "Execution anomaly advice: 1 recommendation(s)."
    )

    assert (
        report.lines[0]
        == (
            "1. unreliable_capability "
            "[system.health]: Inspect dependencies."
        )
    )


def test_advice_report_handles_empty_advice() -> None:
    advice = ExecutionAnomalyAdviceSummary(
        total=0,
        advice=(),
    )

    report = ExecutionAnomalyAdviceReportBuilder().build(
        advice
    )

    assert report.lines == (
        "No anomaly recommendations are currently needed.",
    )
