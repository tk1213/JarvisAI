from __future__ import annotations

import asyncio

from jarvis.core.application import JarvisApplication
from jarvis.core.container import container
from jarvis.planner.ai_plan_adapter import AIPlanAdapter
from jarvis.planner.ai_plan_execution import (
    AIPlanExecutionService,
)
from jarvis.planner.ai_plan_execution_report import (
    AIPlanExecutionReportBuilder,
)
from jarvis.planner.ai_plan_parser import AIPlanParser
from jarvis.planner.ai_plan_pipeline import AIPlanPipeline
from jarvis.planner.ai_plan_validation import AIPlanValidator
from jarvis.planner.executor import PlanExecutor
from jarvis.planner.service import PlannerService
from jarvis.services.capability_registry import CapabilityRegistry


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

        planner = container.resolve(
            "planner",
            PlannerService,
        )

        executor = container.resolve(
            "plan_executor",
            PlanExecutor,
        )

        service = AIPlanExecutionService(
            pipeline=AIPlanPipeline(
                parser=AIPlanParser(),
                adapter=AIPlanAdapter(
                    validator=AIPlanValidator(
                        registry
                    ),
                    planner=planner,
                ),
            ),
            executor=executor,
        )

        result = await service.execute(
            {
                "goal": (
                    "Check whether JarvisAI is responding "
                    "and healthy."
                ),
                "reasoning_summary": (
                    "Execute two read-only system checks."
                ),
                "steps": [
                    {
                        "capability": "system.ping",
                        "arguments": {},
                        "description": (
                            "Verify JarvisAI responsiveness."
                        ),
                    },
                    {
                        "capability": "system.health",
                        "arguments": {},
                        "description": (
                            "Read JarvisAI health."
                        ),
                    },
                ],
            }
        )

        report = AIPlanExecutionReportBuilder().build(
            result
        )

        print(
            "Sprint 4.0 AI Plan Execution"
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

        if not result.success:
            raise RuntimeError(
                "AI plan execution failed."
            )

        if result.completed_steps != 2:
            raise RuntimeError(
                "AI plan completed step count is incorrect."
            )

        print(
            "AI plan execution gate: PASS"
        )

    finally:
        await app.shutdown()


if __name__ == "__main__":
    asyncio.run(
        main()
    )
