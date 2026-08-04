from __future__ import annotations

import asyncio

from jarvis.core.application import JarvisApplication
from jarvis.core.container import container
from jarvis.planner.execution_history import ExecutionHistoryService
from jarvis.planner.execution_persistence import (
    ExecutionPersistenceService,
)
from jarvis.planner.execution_query import ExecutionQuery
from jarvis.services.capability import CapabilityRequest
from jarvis.services.capability_router import CapabilityRouter


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

        history = await history_service.query(
            ExecutionQuery(
                limit=20,
            )
        )

        router = container.resolve(
            "capability_router",
            CapabilityRouter,
        )

        print(
            "Sprint 3.6 End-to-End Observability Gate"
        )
        print(
            "=" * 60
        )

        print(
            "[Gate 1] Execution query"
        )
        print(
            f"Records visible: {history.total}"
        )

        if history.total == 0:
            print()
            print(
                "[Gate 2] Detail / diagnostics"
            )
            print(
                "No persisted execution records are available."
            )
            print(
                "Sprint 3.6 end-to-end gate: PASS "
                "(no-data path)"
            )
            return

        record_id = 1

        detail = await router.execute_request(
            CapabilityRequest(
                capability="system.execution_detail",
                arguments={
                    "record_id": str(
                        record_id
                    ),
                },
            )
        )

        diagnostics = await router.execute_request(
            CapabilityRequest(
                capability="system.execution_diagnostics",
                arguments={
                    "record_id": str(
                        record_id
                    ),
                },
            )
        )

        print()
        print(
            "[Gate 2] Execution detail"
        )
        print(
            f"Available: {detail['available']}"
        )
        print(
            f"Summary: {detail['summary']}"
        )

        print()
        print(
            "[Gate 3] Execution diagnostics"
        )
        print(
            f"Available: {diagnostics['available']}"
        )
        print(
            f"Summary: {diagnostics['summary']}"
        )

        if (
            detail["record_id"] != record_id
            or diagnostics["record_id"] != record_id
        ):
            raise RuntimeError(
                "Execution observability record ID mismatch."
            )

        print()
        print(
            "Sprint 3.6 end-to-end gate: PASS"
        )

    finally:
        await app.shutdown()


if __name__ == "__main__":
    asyncio.run(
        main()
    )
