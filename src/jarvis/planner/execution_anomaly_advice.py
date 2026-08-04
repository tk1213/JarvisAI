from __future__ import annotations

from dataclasses import dataclass

from jarvis.planner.execution_anomalies import (
    ExecutionAnomaly,
    ExecutionAnomalySummary,
)
from jarvis.planner.execution_anomaly_triage import (
    ExecutionAnomalyTriageService,
)


@dataclass(slots=True, frozen=True)
class ExecutionAnomalyAdvice:
    priority: int
    anomaly_code: str
    capability: str | None
    recommendation: str


@dataclass(slots=True, frozen=True)
class ExecutionAnomalyAdviceSummary:
    total: int
    advice: tuple[
        ExecutionAnomalyAdvice,
        ...
    ]


class ExecutionAnomalyAdviceService:
    def __init__(
        self,
        triage: ExecutionAnomalyTriageService | None = None,
    ) -> None:
        self._triage = (
            triage
            if triage is not None
            else ExecutionAnomalyTriageService()
        )

    def build(
        self,
        anomalies: ExecutionAnomalySummary,
    ) -> ExecutionAnomalyAdviceSummary:
        triage = self._triage.prioritize(
            anomalies
        )

        advice = tuple(
            ExecutionAnomalyAdvice(
                priority=item.priority,
                anomaly_code=item.anomaly.code,
                capability=item.anomaly.capability,
                recommendation=self._recommend(
                    item.anomaly
                ),
            )
            for item in triage.items
        )

        return ExecutionAnomalyAdviceSummary(
            total=len(
                advice
            ),
            advice=advice,
        )

    @staticmethod
    def _recommend(
        anomaly: ExecutionAnomaly,
    ) -> str:
        recommendations = {
            "no_execution_history": (
                "Collect more execution history before making "
                "reliability decisions."
            ),
            "low_success_rate": (
                "Review recent failed executions and identify "
                "the dominant failure causes before changing "
                "runtime policy."
            ),
            "degraded_success_rate": (
                "Review recent failures and retries for recurring "
                "patterns."
            ),
            "repeated_timeouts": (
                "Inspect timeout-prone capabilities, dependency "
                "latency, and configured execution deadlines."
            ),
            "execution_timeout": (
                "Inspect the timed-out execution before changing "
                "timeout configuration."
            ),
            "worsening_execution_trend": (
                "Compare the current and previous execution "
                "windows to identify newly introduced failures."
            ),
            "unreliable_capability": (
                "Inspect recent failures for this capability and "
                "verify its dependencies before re-enabling or "
                "changing runtime behavior."
            ),
            "degraded_capability": (
                "Monitor this capability closely and review its "
                "recent retries and failures."
            ),
        }

        return recommendations.get(
            anomaly.code,
            (
                "Review the anomaly and related execution history "
                "before taking manual action."
            ),
        )
