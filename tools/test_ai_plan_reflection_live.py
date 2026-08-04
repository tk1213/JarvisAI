from __future__ import annotations

import asyncio

from jarvis.core.application import JarvisApplication
from jarvis.core.container import container
from jarvis.planner.ai_plan_adapter import AIPlanAdapter
from jarvis.planner.ai_plan_execution import (
    AIPlanExecutionService,
)
from jarvis.planner.ai_plan_parser import AIPlanParser
from jarvis.planner.ai_plan_pipeline import AIPlanPipeline
from jarvis.planner.ai_plan_reflection import (
    AIPlanReflectionDecision,
    AIPlanReflectionService,
)
from jarvis.planner.ai_plan_reflection_report import (
    AIPlanReflectionReportBuilder,
)
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

        execution_service = AIPlanExecutionService(
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

        execution = await execution_service.execute(
            {
                "goal": (
                    "Check whether JarvisAI is responding "
                    "and healthy."
                ),
                "steps": [
                    {
                        "capability": "system.ping",
                        "arguments": {},
                    },
                    {
                        "capability": "system.health",
                        "arguments": {},
                    },
                ],
            }
        )

        reflection = AIPlanReflectionService().reflect(
            execution
        )

        report = AIPlanReflectionReportBuilder().build(
            reflection
        )

        print(
            "Sprint 4.0 AI Plan Reflection"
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

        if (
            reflection.decision
            is not AIPlanReflectionDecision.COMPLETE
        ):
            raise RuntimeError(
                "AI plan reflection did not complete."
            )

        print(
            "AI plan reflection gate: PASS"
        )

    finally:
        await app.shutdown()


if __name__ == "__main__":
    asyncio.run(
        main()
    )
