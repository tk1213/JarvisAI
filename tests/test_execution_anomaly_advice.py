from jarvis.planner.execution_anomalies import (
    ExecutionAnomaly,
    ExecutionAnomalySeverity,
    ExecutionAnomalySummary,
)
from jarvis.planner.execution_anomaly_advice import (
    ExecutionAnomalyAdviceService,
)


def test_advice_follows_triage_priority() -> None:
    anomalies = ExecutionAnomalySummary(
        total=3,
        critical=1,
        warnings=1,
        anomalies=(
            ExecutionAnomaly(
                code="execution_timeout",
                severity=ExecutionAnomalySeverity.WARNING,
                message="timeout",
            ),
            ExecutionAnomaly(
                code="unreliable_capability",
                severity=ExecutionAnomalySeverity.CRITICAL,
                capability="system.health",
                message="unreliable",
            ),
            ExecutionAnomaly(
                code="no_execution_history",
                severity=ExecutionAnomalySeverity.INFO,
                message="no history",
            ),
        ),
    )

    advice = ExecutionAnomalyAdviceService().build(
        anomalies
    )

    assert advice.total == 3
    assert [
        item.anomaly_code
        for item in advice.advice
    ] == [
        "unreliable_capability",
        "execution_timeout",
        "no_execution_history",
    ]

    assert (
        "dependencies"
        in advice.advice[0].recommendation
    )


def test_advice_uses_safe_fallback_for_unknown_code() -> None:
    anomalies = ExecutionAnomalySummary(
        total=1,
        critical=0,
        warnings=1,
        anomalies=(
            ExecutionAnomaly(
                code="future_anomaly",
                severity=ExecutionAnomalySeverity.WARNING,
                message="future",
            ),
        ),
    )

    advice = ExecutionAnomalyAdviceService().build(
        anomalies
    )

    assert (
        advice.advice[0].recommendation
        == (
            "Review the anomaly and related execution history "
            "before taking manual action."
        )
    )


def test_advice_handles_empty_anomalies() -> None:
    anomalies = ExecutionAnomalySummary(
        total=0,
        critical=0,
        warnings=0,
        anomalies=(),
    )

    advice = ExecutionAnomalyAdviceService().build(
        anomalies
    )

    assert advice.total == 0
    assert advice.advice == ()
