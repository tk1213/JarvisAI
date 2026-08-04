from __future__ import annotations

import asyncio

from jarvis.core.application import JarvisApplication
from jarvis.core.container import container
from jarvis.planner.ai_plan_parser import AIPlanParser
from jarvis.planner.ai_plan_schema import (
    build_ai_plan_json_schema,
)
from jarvis.planner.ai_plan_validation import AIPlanValidator
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

        draft = AIPlanParser().parse(
            {
                "goal": "Check whether JarvisAI is healthy.",
                "reasoning_summary": (
                    "Use only read-only system capabilities."
                ),
                "steps": [
                    {
                        "capability": "system.ping",
                        "arguments": {},
                        "description": "Verify responsiveness.",
                    },
                    {
                        "capability": "system.health",
                        "arguments": {},
                        "description": "Read system health.",
                    },
                ],
            }
        )

        validation = AIPlanValidator(
            registry
        ).validate(
            draft
        )

        schema = build_ai_plan_json_schema()

        print(
            "Sprint 4.0 AI Plan Foundation"
        )
        print(
            "-" * 60
        )
        print(
            f"Goal: {draft.goal}"
        )
        print(
            f"Steps: {len(draft.steps)}"
        )
        print(
            f"Valid: {validation.valid}"
        )
        print(
            "Schema additionalProperties: "
            f"{schema['additionalProperties']}"
        )

        if not validation.valid:
            raise RuntimeError(
                "AI plan foundation validation failed."
            )

        print(
            "AI plan foundation gate: PASS"
        )

    finally:
        await app.shutdown()


if __name__ == "__main__":
    asyncio.run(
        main()
    )
