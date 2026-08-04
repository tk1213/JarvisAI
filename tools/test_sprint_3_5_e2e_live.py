from __future__ import annotations

import asyncio

from jarvis.core.application import JarvisApplication
from jarvis.core.container import container
from jarvis.planner.execution_history import ExecutionHistoryService
from jarvis.planner.execution_history_report import (
    ExecutionHistoryReportBuilder,
)
from jarvis.planner.execution_persistence import (
    ExecutionPersistenceService,
)
from jarvis.services.capability import CapabilityRequest
from jarvis.services.capability_registry import CapabilityRegistry
from jarvis.services.capability_router import CapabilityRouter
from jarvis.tools.definitions import ToolDefinitionFactory


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

        registry = container.resolve(
            "capability_registry",
            CapabilityRegistry,
        )

        factory = ToolDefinitionFactory(
            registry
        )

        tool_names = {
            definition.name
            for definition in factory.list_definitions()
        }

        router = container.resolve(
            "capability_router",
            CapabilityRouter,
        )

        capability_result = await router.execute_request(
            CapabilityRequest(
                capability="system.execution_history",
            )
        )

        print(
            "Sprint 3.5 End-to-End Persistence Gate"
        )
        print(
            "=" * 60
        )

        print(
            "[Gate 1] Persistent execution history"
        )
        print(
            report.summary
        )

        print()
        print(
            "[Gate 2] Native tool surface"
        )
        print(
            "system_execution_history present: "
            f"{'system_execution_history' in tool_names}"
        )

        print()
        print(
            "[Gate 3] Runtime capability read"
        )
        print(
            f"Available: {capability_result['available']}"
        )
        print(
            f"Summary: {capability_result['summary']}"
        )

        if (
            "system_execution_history"
            not in tool_names
        ):
            raise RuntimeError(
                "Execution history native tool is missing."
            )

        if not capability_result[
            "available"
        ]:
            raise RuntimeError(
                "Execution history capability is unavailable."
            )

        print()
        print(
            "Sprint 3.5 end-to-end gate: PASS"
        )

    finally:
        await app.shutdown()


if __name__ == "__main__":
    asyncio.run(
        main()
    )
