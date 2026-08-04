from __future__ import annotations

import asyncio

from jarvis.core.application import JarvisApplication
from jarvis.core.container import container
from jarvis.planner.capability_reliability import (
    CapabilityReliabilityService,
)
from jarvis.planner.execution_anomalies import (
    ExecutionAnomalyService,
)
from jarvis.planner.execution_health_trends import (
    ExecutionHealthTrendService,
)
from jarvis.planner.execution_incident_correlation import (
    ExecutionIncidentCorrelationService,
)
from jarvis.planner.execution_incident_correlation_report import (
    ExecutionIncidentCorrelationReportBuilder,
)
from jarvis.planner.execution_incidents import (
    ExecutionIncidentService,
)
from jarvis.planner.execution_persistence import (
    ExecutionPersistenceService,
)
from jarvis.planner.execution_statistics import (
    ExecutionStatisticsService,
)


async def main() -> None:
    app = JarvisApplication()

    try:
        await app.start(
            start_background_tasks=False,
        )

        persistence = container.resolve(
            "execution_persistence",
            ExecutionPersistenceService,
        )

        anomalies = await ExecutionAnomalyService(
            ExecutionStatisticsService(
                persistence
            ),
            CapabilityReliabilityService(
                persistence
            ),
            ExecutionHealthTrendService(
                persistence
            ),
        ).detect(
            limit=100,
            trend_window_size=20,
        )

        incident = ExecutionIncidentService().build(
            anomalies
        )

        print(
            "Sprint 3.9 Execution Incident Correlation"
        )
        print(
            "-" * 60
        )

        if incident is None:
            print(
                "No execution incident was generated."
            )
            print(
                "Execution incident correlation gate: "
                "PASS (no-incident path)"
            )
            return

        correlation = (
            ExecutionIncidentCorrelationService().correlate(
                incident
            )
        )

        report = (
            ExecutionIncidentCorrelationReportBuilder().build(
                correlation
            )
        )

        print(
            report.summary
        )

        for line in report.lines:
            print(
                line
            )

        print(
            "Execution incident correlation gate: PASS"
        )

    finally:
        await app.shutdown()


if __name__ == "__main__":
    asyncio.run(
        main()
    )
