from __future__ import annotations

import pytest

from jarvis.planner.execution_anomalies import (
    ExecutionAnomaly,
    ExecutionAnomalySeverity,
    ExecutionAnomalySummary,
)
from jarvis.planner.execution_anomaly_advice import (
    ExecutionAnomalyAdviceService,
)
from jarvis.planner.execution_anomaly_triage import (
    ExecutionAnomalyTriageService,
)


@pytest.mark.asyncio
async def test_anomaly_triage_and_advice_work_together() -> None:
    anomalies = ExecutionAnomalySummary(
        total=3,
        critical=1,
        warnings=1,
        anomalies=(
            ExecutionAnomaly(
                code="execution_timeout",
                severity=ExecutionAnomalySeverity.WARNING,
                message="Timeout detected.",
            ),
            ExecutionAnomaly(
                code="unreliable_capability",
                severity=ExecutionAnomalySeverity.CRITICAL,
                capability="system.health",
                message="Capability reliability is low.",
            ),
            ExecutionAnomaly(
                code="no_execution_history",
                severity=ExecutionAnomalySeverity.INFO,
                message="No history.",
            ),
        ),
    )

    triage = ExecutionAnomalyTriageService().prioritize(
        anomalies
    )

    advice = ExecutionAnomalyAdviceService().build(
        anomalies
    )

    assert triage.total == 3
    assert advice.total == 3

    assert triage.items[0].anomaly.code == (
        "unreliable_capability"
    )

    assert advice.advice[0].anomaly_code == (
        "unreliable_capability"
    )

    assert (
        triage.items[0].priority
        == advice.advice[0].priority
        == 1
    )
