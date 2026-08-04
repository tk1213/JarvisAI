from __future__ import annotations

import asyncio
from dataclasses import replace
from datetime import timedelta

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
from jarvis.planner.execution_incident_timeline import (
    ExecutionIncidentTimelineService,
)
from jarvis.planner.execution_incident_timeline_report import (
    ExecutionIncidentTimelineReportBuilder,
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
            "Sprint 3.9 Execution Incident Timeline"
        )
        print(
            "-" * 60
        )

        if incident is None:
            print(
                "No execution incident was generated."
            )
            print(
                "Execution incident timeline gate: "
                "PASS (no-incident path)"
            )
            return

        correlation = (
            ExecutionIncidentCorrelationService().correlate(
                incident
            )
        )

        earlier_incident = replace(
            incident,
            incident_id=(
                incident.incident_id
                + "-previous"
            ),
            created_at=(
                incident.created_at
                - timedelta(
                    hours=2
                )
            ),
        )

        timeline = ExecutionIncidentTimelineService().build(
            fingerprint=correlation.fingerprint,
            incidents=[
                incident,
                earlier_incident,
            ],
            now=incident.created_at,
        )

        if timeline is None:
            raise RuntimeError(
                "Execution incident timeline was not generated."
            )

        report = ExecutionIncidentTimelineReportBuilder().build(
            timeline
        )

        print(
            report.summary
        )

        for line in report.lines:
            print(
                line
            )

        if timeline.occurrence_count != 2:
            raise RuntimeError(
                "Timeline occurrence count is incorrect."
            )

        print(
            "Execution incident timeline gate: PASS"
        )

    finally:
        await app.shutdown()


if __name__ == "__main__":
    asyncio.run(
        main()
    )
