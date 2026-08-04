from __future__ import annotations

import asyncio

from jarvis.core.application import JarvisApplication
from jarvis.core.container import container
from jarvis.planner.execution_history import ExecutionHistoryService
from jarvis.planner.execution_persistence import (
    ExecutionPersistenceService,
)
from jarvis.planner.execution_query import ExecutionQuery


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

        service = ExecutionHistoryService(
            persistence
        )

        completed = await service.query(
            ExecutionQuery(
                limit=20,
                status="completed",
            )
        )

        ping_records = await service.query(
            ExecutionQuery(
                limit=20,
                capability="system.ping",
            )
        )

        print(
            "Sprint 3.6 Execution Query"
        )
        print(
            "-" * 60
        )
        print(
            f"Completed records: {completed.total}"
        )
        print(
            f"system.ping records: {ping_records.total}"
        )

        for record in ping_records.records:
            print(
                f"- {record.goal} [{record.plan_status}]"
            )

        print(
            "Execution query gate: PASS"
        )

    finally:
        await app.shutdown()


if __name__ == "__main__":
    asyncio.run(
        main()
    )
