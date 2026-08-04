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

        print(
            "Sprint 3.9 End-to-End Incident Intelligence Gate"
        )
        print(
            "=" * 60
        )

        print(
            "[Gate 1] Incident snapshot"
        )
        print(
            f"Generated: {incident is not None}"
        )

        if incident is not None:
            correlation = (
                ExecutionIncidentCorrelationService().correlate(
                    incident
                )
            )

            correlations.append(
                correlation
            )

            print()
            print(
                "[Gate 2] Correlation"
            )
            print(
                f"Fingerprint: {correlation.fingerprint}"
            )

            timeline = ExecutionIncidentTimelineService().build(
                fingerprint=correlation.fingerprint,
                incidents=[
                    incident
                ],
                now=incident.created_at,
            )

            if timeline is None:
                raise RuntimeError(
                    "Incident timeline was not generated."
                )

            timelines.append(
                timeline
            )

            print()
            print(
                "[Gate 3] Timeline"
            )
            print(
                f"Occurrences: {timeline.occurrence_count}"
            )
            print(
                f"Latest severity: {timeline.latest_severity}"
            )

        else:
            print()
            print(
                "[Gate 2] Correlation"
            )
            print(
                "No incident available."
            )

            print()
            print(
                "[Gate 3] Timeline"
            )
            print(
                "No incident available."
            )

        grouping = ExecutionIncidentGroupingService().group(
            correlations
        )

        print()
        print(
            "[Gate 4] Grouping"
        )
        print(
            f"Incidents: {grouping.total_incidents}"
        )
        print(
            f"Groups: {grouping.total_groups}"
        )

        snapshot = ExecutionIncidentDashboardService().build(
            grouping=grouping,
            timelines=timelines,
        )

        report = ExecutionIncidentDashboardReportBuilder().build(
            snapshot
        )

        print()
        print(
            "[Gate 5] Dashboard"
        )
        print(
            report.summary
        )

        for line in report.lines:
            print(
                line
            )

        if incident is not None:
            if grouping.total_incidents != 1:
                raise RuntimeError(
                    "Incident grouping count is incorrect."
                )

            if snapshot.total_incidents != 1:
                raise RuntimeError(
                    "Dashboard incident count is incorrect."
                )

        print()
        print(
            "Sprint 3.9 end-to-end gate: PASS"
        )

    finally:
        await app.shutdown()


if __name__ == "__main__":
    asyncio.run(
        main()
    )
