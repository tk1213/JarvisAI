from __future__ import annotations

from dataclasses import dataclass, field

import pytest

from jarvis.planner.ai_generator import AIPlanGenerator
from jarvis.planner.service import PlannerService
from jarvis.services.capability import CapabilityDefinition


@dataclass
class StubAI:
    response: str
    prompts: list[str] = field(
        default_factory=list
    )

    async def ask(
        self,
        text: str,
        history=None,
    ) -> str:
        del history
        self.prompts.append(
            text
        )
        return self.response


class StubRegistry:
    def __init__(self) -> None:
        self._definitions = [
            CapabilityDefinition(
                name="smart_home.turn_off",
                description="Turn off a smart-home device.",
                arguments={
                    "device": "Device name",
                },
            ),
            CapabilityDefinition(
                name="smart_home.status",
                description="Read smart-home device status.",
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


def build_generator(
    response: str,
) -> AIPlanGenerator:
    registry = StubRegistry()
    planner = PlannerService(
        registry,  # type: ignore[arg-type]
    )

    return AIPlanGenerator(
        ai=StubAI(response),  # type: ignore[arg-type]
        registry=registry,  # type: ignore[arg-type]
        planner=planner,
    )


@pytest.mark.asyncio
async def test_generate_multi_step_plan() -> None:
    generator = build_generator(
        """
        {
          "steps": [
            {
              "capability": "smart_home.turn_off",
              "arguments": {"device": "bedroom light"}
            },
            {
              "capability": "smart_home.status",
              "arguments": {"device": "bedroom light"}
            }
          ]
        }
        """
    )

    plan = await generator.generate(
        "Turn off bedroom light and check status"
    )

    assert plan is not None
    assert len(plan.steps) == 2
    assert (
        plan.steps[0].capability
        == "smart_home.turn_off"
    )
    assert (
        plan.steps[1].capability
        == "smart_home.status"
    )


@pytest.mark.asyncio
async def test_generate_none_for_empty_steps() -> None:
    generator = build_generator(
        '{"steps":[]}'
    )

    plan = await generator.generate(
        "Tell me a joke"
    )

    assert plan is None


@pytest.mark.asyncio
async def test_invalid_json_returns_none() -> None:
    generator = build_generator(
        "not-json"
    )

    plan = await generator.generate(
        "Turn off bedroom light"
    )

    assert plan is None


@pytest.mark.asyncio
async def test_disallowed_capability_is_rejected() -> None:
    generator = build_generator(
        """
        {
          "steps": [
            {
              "capability": "dangerous.unknown",
              "arguments": {}
            }
          ]
        }
        """
    )

    with pytest.raises(
        PermissionError,
        match="not allowed",
    ):
        await generator.generate(
            "Do something unsupported"
        )


@pytest.mark.asyncio
async def test_max_steps_is_enforced() -> None:
    registry = StubRegistry()
    planner = PlannerService(
        registry,  # type: ignore[arg-type]
    )
    ai = StubAI(
        """
        {
          "steps": [
            {"capability":"smart_home.status","arguments":{}},
            {"capability":"smart_home.status","arguments":{}}
          ]
        }
        """
    )

    generator = AIPlanGenerator(
        ai=ai,  # type: ignore[arg-type]
        registry=registry,  # type: ignore[arg-type]
        planner=planner,
        max_steps=1,
    )

    with pytest.raises(
        ValueError,
        match="maximum step",
    ):
        await generator.generate(
            "Check twice"
        )
