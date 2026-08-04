from __future__ import annotations

import asyncio

from jarvis.core.application import JarvisApplication
from jarvis.core.container import container
from jarvis.planner.ai_plan_adapter import AIPlanAdapter
from jarvis.planner.ai_plan_parser import AIPlanParser
from jarvis.planner.ai_plan_pipeline import AIPlanPipeline
from jarvis.planner.ai_plan_validation import AIPlanValidator
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

        pipeline = AIPlanPipeline(
            parser=AIPlanParser(),
            adapter=AIPlanAdapter(
                validator=AIPlanValidator(
                    registry
                ),
                planner=planner,
            ),
        )

        result = pipeline.build(
            {
                "goal": (
                    "Check whether JarvisAI is responding "
                    "and healthy."
                ),
                "reasoning_summary": (
                    "Use two safe read-only system checks."
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
                            "Read JarvisAI health status."
                        ),
                    },
                ],
            }
        )

        plan = result.adaptation.plan

        print(
            "Sprint 4.0 AI Plan Adapter Pipeline"
        )
        print(
            "-" * 60
        )
        print(
            f"Goal: {plan.goal}"
        )
        print(
            f"Steps: {len(plan.steps)}"
        )
        print(
            f"Validation: {result.adaptation.validation.valid}"
        )

        for index, step in enumerate(
            plan.steps,
            start=1,
        ):
            print(
                f"{index}. {step.capability} "
                f"arguments={step.arguments}"
            )

        if not result.adaptation.validation.valid:
            raise RuntimeError(
                "AI plan pipeline validation failed."
            )

        print(
            "AI plan adapter pipeline gate: PASS"
        )

    finally:
        await app.shutdown()


if __name__ == "__main__":
    asyncio.run(
        main()
    )
