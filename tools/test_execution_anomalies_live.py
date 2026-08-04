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
from jarvis.planner.execution_anomaly_report import (
    ExecutionAnomalyReportBuilder,
)
from jarvis.planner.execution_health_trends import (
    ExecutionHealthTrendService,
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

        statistics = ExecutionStatisticsService(
            persistence
        )
        reliability = CapabilityReliabilityService(
            persistence
        )
        trends = ExecutionHealthTrendService(
            persistence
        )

        service = ExecutionAnomalyService(
            statistics,
            reliability,
            trends,
        )

        anomalies = await service.detect(
            limit=100,
            trend_window_size=20,
        )

        report = ExecutionAnomalyReportBuilder().build(
            anomalies
        )

        print(
            "Sprint 3.8 Execution Anomalies"
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
            "Execution anomaly gate: PASS"
        )

    finally:
        await app.shutdown()


if __name__ == "__main__":
    asyncio.run(
        main()
    )
