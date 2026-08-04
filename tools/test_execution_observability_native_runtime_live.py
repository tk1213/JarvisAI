from __future__ import annotations

import asyncio

from jarvis.core.application import JarvisApplication
from jarvis.core.container import container
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

        recent = await persistence.list_recent(
            limit=1
        )

        runner = container.get(
            "openai_tool_runner"
        )

        print(
            "Sprint 3.6 Native Observability Runtime"
        )
        print(
            "-" * 60
        )
        print(
            "OpenAI tool runner registered: "
            f"{runner is not None}"
        )

        if runner is None:
            raise RuntimeError(
                "Native OpenAI tool runner is not registered."
            )

        if not recent:
            print(
                "No persisted execution records are available."
            )
            print(
                "Native observability runtime gate: "
                "PASS (no-data path)"
            )
            return

        print(
            "Persisted execution history is available."
        )
        print(
            "Native observability runtime gate: PASS"
        )

    finally:
        await app.shutdown()


if __name__ == "__main__":
    asyncio.run(
        main()
    )
