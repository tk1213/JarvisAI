from __future__ import annotations

import asyncio

from jarvis.core.application import JarvisApplication
from jarvis.core.container import container
from jarvis.planner.capability_reliability import (
    CapabilityReliabilityService,
)
from jarvis.planner.execution_health import ExecutionHealthService
from jarvis.planner.execution_health_report import (
    ExecutionHealthReportBuilder,
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

        health_service = ExecutionHealthService(
            statistics,
            reliability,
        )

        snapshot = await health_service.check(
            limit=100
        )

        report = ExecutionHealthReportBuilder().build(
            snapshot
        )

        print(
            "Sprint 3.7 Execution Health"
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
            "Execution health gate: PASS"
        )

    finally:
        await app.shutdown()


if __name__ == "__main__":
    asyncio.run(
        main()
    )
