from __future__ import annotations

import asyncio

from jarvis.core.application import JarvisApplication
from jarvis.core.container import container
from jarvis.planner.ai_generator import AIPlanGenerator
from jarvis.planner.executor import PlanExecutor
from jarvis.planner.service import PlannerService
from jarvis.services.capability_registry import CapabilityRegistry
from jarvis.services.capability_router import CapabilityRouter


async def main() -> None:
    app = JarvisApplication()

    try:
        await app.start(
            start_background_tasks=False,
        )

        registry = container.resolve(
            "capability_registry",
            CapabilityRegistry,
        )
        router = container.resolve(
            "capability_router",
            CapabilityRouter,
        )
        planner = container.resolve(
            "planner",
            PlannerService,
        )
        executor = container.resolve(
            "plan_executor",
            PlanExecutor,
        )
        generator = container.resolve(
            "ai_plan_generator",
            AIPlanGenerator,
        )

        print(
            "Planner DI runtime"
        )
        print(
            "-" * 60
        )
        print(
            f"Capabilities: {len(registry)}"
        )
        print(
            "planner registry shared: "
            f"{planner._registry is registry}"
        )
        print(
            "router registry shared: "
            f"{router._registry is registry}"
        )
        print(
            "generator registry shared: "
            f"{generator._registry is registry}"
        )
        print(
            "executor router shared: "
            f"{executor._router is router}"
        )
        print()
        print(
            "Registered capabilities:"
        )

        for capability in registry.list_capabilities():
            print(
                f"- {capability}"
            )

    finally:
        await app.shutdown()


if __name__ == "__main__":
    asyncio.run(
        main()
    )
