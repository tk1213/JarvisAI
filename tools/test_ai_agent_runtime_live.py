from __future__ import annotations

import asyncio

from jarvis.agent.report import (
    AIAgentRunReportBuilder,
)
from jarvis.agent.runtime import (
    AIAgentRunStatus,
    AIAgentRuntime,
)
from jarvis.core.application import JarvisApplication
from jarvis.core.container import container
from jarvis.planner.ai_plan_memory import (
    AIPlanMemoryStore,
)
from jarvis.planner.ai_plan_reflection import (
    AIPlanReflectionService,
)
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

        runtime = AIAgentRuntime(
            orchestrator=orchestrator,
            reflection=AIPlanReflectionService(),
            memory=AIPlanMemoryStore(),
        )

        result = await runtime.run(
            
                "Check whether JarvisAI is responding "
                "and healthy using read-only capabilities."
            
        )

        report = AIAgentRunReportBuilder().build(
            result
        )

        print(
            "Sprint 4.0 AI Agent Runtime"
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

        if result.status is AIAgentRunStatus.NO_PLAN:
            raise RuntimeError(
                "The live AI agent did not produce a plan."
            )

        if result.requires_confirmation:
            raise RuntimeError(
                "The read-only live plan unexpectedly "
                "requires confirmation."
            )

        if not result.success:
            raise RuntimeError(
                "The live AI agent execution failed."
            )

        print(
            "AI agent runtime gate: PASS"
        )

    finally:
        await app.shutdown()


if __name__ == "__main__":
    asyncio.run(
        main()
    )
