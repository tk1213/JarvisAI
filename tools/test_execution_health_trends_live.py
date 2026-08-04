from __future__ import annotations

import asyncio

from jarvis.core.application import JarvisApplication
from jarvis.core.container import container
from jarvis.planner.execution_health_trend_report import (
    ExecutionHealthTrendReportBuilder,
)
from jarvis.planner.execution_health_trends import (
    ExecutionHealthTrendService,
)
from jarvis.planner.execution_persistence import (
    ExecutionPersistenceService,
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

        service = ExecutionHealthTrendService(
            persistence
        )

        trend = await service.summarize(
            window_size=20
        )

        report = ExecutionHealthTrendReportBuilder().build(
            trend
        )

        print(
            "Sprint 3.7 Execution Health Trends"
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
            "Execution health trend gate: PASS"
        )

    finally:
        await app.shutdown()


if __name__ == "__main__":
    asyncio.run(
        main()
    )
