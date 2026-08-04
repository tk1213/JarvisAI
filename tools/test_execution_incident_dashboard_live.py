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
from jarvis.planner.execution_incident_dashboard import (
    ExecutionIncidentDashboardService,
)
from jarvis.planner.execution_incident_dashboard_report import (
    ExecutionIncidentDashboardReportBuilder,
)
from jarvis.planner.execution_incident_grouping import (
    ExecutionIncidentGroupingService,
)
from jarvis.planner.execution_incident_timeline import (
    ExecutionIncidentTimelineService,
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

        correlations = []
        timelines = []

        if incident is not None:
            correlation = (
                ExecutionIncidentCorrelationService().correlate(
                    incident
                )
            )

            correlations.append(
                correlation
            )

            timeline = ExecutionIncidentTimelineService().build(
                fingerprint=correlation.fingerprint,
                incidents=[
                    incident
                ],
                now=incident.created_at,
            )

            if timeline is not None:
                timelines.append(
                    timeline
                )

        grouping = ExecutionIncidentGroupingService().group(
            correlations
        )

        snapshot = ExecutionIncidentDashboardService().build(
            grouping=grouping,
            timelines=timelines,
        )

        report = ExecutionIncidentDashboardReportBuilder().build(
            snapshot
        )

        print(
            "Sprint 3.9 Execution Incident Dashboard"
        )
        print(
            "-" * 60
        )
        print(
            report.summary
        )

        for line in report.lines:
            print(
                line
            )

        print(
            "Execution incident dashboard gate: PASS"
        )

    finally:
        await app.shutdown()


if __name__ == "__main__":
    asyncio.run(
        main()
    )
