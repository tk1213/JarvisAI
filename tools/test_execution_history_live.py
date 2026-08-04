from __future__ import annotations

import asyncio

from jarvis.core.application import JarvisApplication
from jarvis.core.container import container
from jarvis.planner.execution_history import (
    ExecutionHistoryService,
)
from jarvis.planner.execution_history_report import (
    ExecutionHistoryReportBuilder,
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

        history_service = ExecutionHistoryService(
            persistence
        )

        history = await history_service.recent(
            limit=10
        )

        report = ExecutionHistoryReportBuilder().build(
            history
        )

        print(
            "Sprint 3.5 Execution History"
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
            "Execution history gate: PASS"
        )

    finally:
        await app.shutdown()


if __name__ == "__main__":
    asyncio.run(
        main()
    )
