from __future__ import annotations

import asyncio

from jarvis.core.application import JarvisApplication
from jarvis.core.container import container
from jarvis.planner.execution_persistence import (
    ExecutionPersistenceService,
)
from jarvis.planner.execution_statistics import (
    ExecutionStatisticsService,
)
from jarvis.planner.execution_statistics_report import (
    ExecutionStatisticsReportBuilder,
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

        statistics_service = ExecutionStatisticsService(
            persistence
        )

        statistics = await statistics_service.summarize(
            limit=100
        )

        report = ExecutionStatisticsReportBuilder().build(
            statistics
        )

        print(
            "Sprint 3.7 Execution Statistics"
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
            "Execution statistics gate: PASS"
        )

    finally:
        await app.shutdown()


if __name__ == "__main__":
    asyncio.run(
        main()
    )
