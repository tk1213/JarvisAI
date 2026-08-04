from __future__ import annotations

import asyncio

from jarvis.core.application import JarvisApplication
from jarvis.core.container import container
from jarvis.planner.orchestrator import PlannerOrchestrator


async def main() -> None:
    app = JarvisApplication()

    try:
        await app.start(
            start_background_tasks=False,
        )

        orchestrator = container.resolve(
            "planner_orchestrator",
            PlannerOrchestrator,
        )

        text = (
            "Check the status of Smart Plug 1"
        )

        preview = await orchestrator.prepare(
            text
        )

        if preview is None:
            print(
                "No valid plan generated."
            )
            return

        print(
            f"Goal: {preview.plan.goal}"
        )
        print(
            "Requires confirmation: "
            f"{preview.requires_confirmation}"
        )

        for step in preview.plan.steps:
            print(
                f"{step.index}. "
                f"{step.capability} "
                f"{step.arguments}"
            )

        if preview.requires_confirmation:
            print(
                "Plan not executed because confirmation "
                "is required."
            )
            return

        result = await orchestrator.execute_preview(
            preview
        )

        print(
            f"Execution success: {result.success}"
        )

    finally:
        await app.shutdown()


if __name__ == "__main__":
    asyncio.run(
        main()
    )
