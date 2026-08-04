from __future__ import annotations

import asyncio

from jarvis.planner.ai_generator import AIPlanGenerator
from jarvis.planner.service import PlannerService
from jarvis.services.ai_service import AIService
from jarvis.services.capability import CapabilityDefinition


class DemoRegistry:
    def __init__(self) -> None:
        self._definitions = [
            CapabilityDefinition(
                name="smart_home.turn_off",
                description="Turn off a device.",
                arguments={
                    "device": "Device name",
                },
            ),
            CapabilityDefinition(
                name="smart_home.status",
                description="Read device status.",
                arguments={
                    "device": "Device name",
                },
            ),
        ]

    def list_definitions(
        self,
    ) -> list[CapabilityDefinition]:
        return list(
            self._definitions
        )

    def is_allowed(
        self,
        capability: str,
    ) -> bool:
        return any(
            definition.name == capability
            for definition in self._definitions
        )


async def main() -> None:
    registry = DemoRegistry()

    planner = PlannerService(
        registry,  # type: ignore[arg-type]
    )

    generator = AIPlanGenerator(
        ai=AIService(),
        registry=registry,  # type: ignore[arg-type]
        planner=planner,
    )

    text = (
        "Turn off the bedroom light "
        "and then check its status."
    )

    plan = await generator.generate(
        text
    )

    if plan is None:
        print(
            "No plan generated."
        )
        return

    print(
        f"Goal: {plan.goal}"
    )
    print(
        f"Status: {plan.status.value}"
    )

    for step in plan.steps:
        print(
            f"{step.index}. "
            f"{step.capability} "
            f"{step.arguments}"
        )


if __name__ == "__main__":
    asyncio.run(
        main()
    )
