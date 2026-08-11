from __future__ import annotations

import asyncio

from jarvis.agent.runtime import AIAgentRuntime
from jarvis.agent.session import AIAgentSessionService
from jarvis.agent.session_report import (
    AIAgentSessionReportBuilder,
)
from jarvis.core.application import JarvisApplication
from jarvis.core.container import container
from jarvis.planner.ai_plan_memory import AIPlanMemoryStore


async def main() -> None:
    app = JarvisApplication()

    try:
        await app.start(
            start_background_tasks=False,
        )

        runtime = container.resolve(
            "ai_agent_runtime",
            AIAgentRuntime,
        )

        memory = container.resolve(
            "ai_plan_memory",
            AIPlanMemoryStore,
        )

        snapshot = AIAgentSessionService(
            runtime=runtime,
            memory=memory,
        ).snapshot()

        report = AIAgentSessionReportBuilder().build(
            snapshot
        )

        print(
            "Sprint 4.1 AI Agent Session Snapshot"
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
            "AI agent session snapshot gate: PASS"
        )

    finally:
        await app.shutdown()


if __name__ == "__main__":
    asyncio.run(
        main()
    )
