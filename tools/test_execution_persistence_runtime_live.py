from __future__ import annotations

import asyncio

from jarvis.core.application import JarvisApplication
from jarvis.core.container import container
from jarvis.planner.execution_persistence import (
    ExecutionPersistenceService,
)
from jarvis.planner.executor import PlanExecutor
from jarvis.planner.models import (
    Plan,
    PlanStatus,
    PlanStep,
)


async def main() -> None:
    app = JarvisApplication()

    try:
        await app.start(
            start_background_tasks=False,
        )

        executor = container.resolve(
            "plan_executor",
            PlanExecutor,
        )

        persistence = container.resolve(
            "execution_persistence",
            ExecutionPersistenceService,
        )

        before = await persistence.list_recent(
            limit=100
        )

        plan = Plan(
            goal="Sprint 3.5 runtime persistence gate",
            steps=[
                PlanStep(
                    index=1,
                    capability="system.ping",
                )
            ],
            status=PlanStatus.READY,
        )

        result = await executor.execute(
            plan
        )

        after = await persistence.list_recent(
            limit=100
        )

        print(
            "Sprint 3.5 Runtime Persistence Wiring"
        )
        print(
            "-" * 60
        )
        print(
            "Persistence registered: "
            f"{container.has('execution_persistence')}"
        )
        print(
            f"Plan status: {result.plan.status.value}"
        )
        print(
            f"Records before: {len(before)}"
        )
        print(
            f"Records after: {len(after)}"
        )

        if not result.success:
            raise RuntimeError(
                "Runtime execution failed."
            )

        if len(
            after
        ) != len(
            before
        ) + 1:
            raise RuntimeError(
                "Execution was not persisted automatically."
            )

        if (
            after[0].goal
            != "Sprint 3.5 runtime persistence gate"
        ):
            raise RuntimeError(
                "Latest persisted execution is incorrect."
            )

        print(
            "Runtime persistence wiring gate: PASS"
        )

    finally:
        await app.shutdown()


if __name__ == "__main__":
    asyncio.run(
        main()
    )
