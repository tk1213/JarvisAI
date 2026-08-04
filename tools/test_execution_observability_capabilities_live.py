from __future__ import annotations

import asyncio

from jarvis.core.application import JarvisApplication
from jarvis.core.container import container
from jarvis.planner.execution_persistence import (
    ExecutionPersistenceService,
)
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

        recent = await persistence.list_recent(
            limit=1
        )

        print(
            "Sprint 3.6 Execution Observability Capabilities"
        )
        print(
            "-" * 60
        )

        if not recent:
            print(
                "No persisted execution records are available."
            )
            print(
                "Capability wiring gate: PASS (no-data path)"
            )
            return

        router = container.resolve(
            "capability_router",
            CapabilityRouter,
        )

        # list_recent does not expose IDs in the current persistence DTO.
        # Use record 1 as the oldest known persisted record for this
        # diagnostic and accept a clean not-found response if it was
        # removed from the database.
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

        print(
            f"Detail available: {detail['available']}"
        )
        print(
            f"Detail summary: {detail['summary']}"
        )
        print(
            "Diagnostics available: "
            f"{diagnostics['available']}"
        )
        print(
            "Diagnostics summary: "
            f"{diagnostics['summary']}"
        )

        if (
            detail["record_id"] != record_id
            or diagnostics["record_id"] != record_id
        ):
            raise RuntimeError(
                "Execution observability record ID mismatch."
            )

        print(
            "Execution observability capability gate: PASS"
        )

    finally:
        await app.shutdown()


if __name__ == "__main__":
    asyncio.run(
        main()
    )
