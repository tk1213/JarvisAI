from __future__ import annotations

from unittest.mock import AsyncMock, Mock

import pytest

from jarvis.services.ai_capability_resolver import AICapabilityResolver
from jarvis.services.ai_service import AIService
from jarvis.services.capability import CapabilityDefinition
from jarvis.services.capability_registry import CapabilityRegistry


@pytest.fixture
def registry() -> CapabilityRegistry:
    return CapabilityRegistry(
        {
            "system.health",
            "system.ping",
            "system.version",
        }
    )


def create_ai(
    response: str,
) -> Mock:
    ai = Mock(spec=AIService)
    ai.ask = AsyncMock(
        return_value=response,
    )
    return ai


@pytest.mark.asyncio
async def test_resolve_valid_capability(
    registry: CapabilityRegistry,
) -> None:
    ai = create_ai(
        '{"capability":"system.version","arguments":{}}'
    )

    resolver = AICapabilityResolver(
        ai=ai,
        registry=registry,
    )

    request = await resolver.resolve(
        "Jarvis ใช้เวอร์ชันอะไร",
    )

    assert request is not None
    assert request.capability == "system.version"
    assert request.arguments == {}


@pytest.mark.asyncio
async def test_reject_unknown_capability(
    registry: CapabilityRegistry,
) -> None:
    ai = create_ai(
        '{"capability":"system.delete_everything",'
        '"arguments":{}}'
    )

    resolver = AICapabilityResolver(
        ai=ai,
        registry=registry,
    )

    request = await resolver.resolve(
        "ลบระบบทั้งหมด",
    )

    assert request is None


@pytest.mark.asyncio
async def test_reject_invalid_json(
    registry: CapabilityRegistry,
) -> None:
    ai = create_ai(
        "system.version"
    )

    resolver = AICapabilityResolver(
        ai=ai,
        registry=registry,
    )

    request = await resolver.resolve(
        "Jarvis version",
    )

    assert request is None


@pytest.mark.asyncio
async def test_null_capability_returns_none(
    registry: CapabilityRegistry,
) -> None:
    ai = create_ai(
        '{"capability":null,"arguments":{}}'
    )

    resolver = AICapabilityResolver(
        ai=ai,
        registry=registry,
    )

    request = await resolver.resolve(
        "อธิบาย quantum computing",
    )

    assert request is None


@pytest.mark.asyncio
async def test_resolve_arguments(
    registry: CapabilityRegistry,
) -> None:
    ai = create_ai(
        '{"capability":"system.ping",'
        '"arguments":{"verbose":true}}'
    )

    resolver = AICapabilityResolver(
        ai=ai,
        registry=registry,
    )

    request = await resolver.resolve(
        "ตรวจสอบระบบแบบละเอียด",
    )

    assert request is not None
    assert request.capability == "system.ping"
    assert request.arguments == {
        "verbose": True,
    }


@pytest.mark.asyncio
async def test_empty_text_does_not_call_ai(
    registry: CapabilityRegistry,
) -> None:
    ai = create_ai(
        '{"capability":"system.ping","arguments":{}}'
    )

    resolver = AICapabilityResolver(
        ai=ai,
        registry=registry,
    )

    request = await resolver.resolve("   ")

    assert request is None
    ai.ask.assert_not_awaited()


@pytest.mark.asyncio
async def test_empty_registry_does_not_call_ai() -> None:
    ai = create_ai(
        '{"capability":"system.ping","arguments":{}}'
    )

    resolver = AICapabilityResolver(
        ai=ai,
        registry=CapabilityRegistry(),
    )

    request = await resolver.resolve(
        "ตรวจสอบระบบ",
    )

    assert request is None
    ai.ask.assert_not_awaited()

@pytest.mark.asyncio
async def test_resolve_json_code_fence(
    registry: CapabilityRegistry,
) -> None:
    ai = create_ai(
        "```json\n"
        '{"capability":"system.version","arguments":{}}\n'
        "```"
    )

    resolver = AICapabilityResolver(
        ai=ai,
        registry=registry,
    )

    request = await resolver.resolve(
        "Jarvis version",
    )

    assert request is not None
    assert request.capability == "system.version"


@pytest.mark.asyncio
async def test_reject_non_dict_arguments(
    registry: CapabilityRegistry,
) -> None:
    ai = create_ai(
        '{"capability":"system.version",'
        '"arguments":["invalid"]}'
    )

    resolver = AICapabilityResolver(
        ai=ai,
        registry=registry,
    )

    request = await resolver.resolve(
        "Jarvis version",
    )

    assert request is None


@pytest.mark.asyncio
async def test_reject_json_array(
    registry: CapabilityRegistry,
) -> None:
    ai = create_ai(
        '["system.version"]'
    )

    resolver = AICapabilityResolver(
        ai=ai,
        registry=registry,
    )

    request = await resolver.resolve(
        "Jarvis version",
    )

    assert request is None

def test_build_prompt_includes_description() -> None:
    definitions = [
        CapabilityDefinition(
            name="system.version",
            description="Get the current JarvisAI version.",
        )
    ]

    prompt = AICapabilityResolver._build_prompt(
        text="What version is Jarvis?",
        definitions=definitions,
    )

    assert "Name: system.version" in prompt
    assert (
        "Description: Get the current JarvisAI version."
        in prompt
    )
    assert "Arguments: none" in prompt


def test_build_prompt_includes_arguments() -> None:
    definitions = [
        CapabilityDefinition(
            name="smart_home.light.turn_on",
            description="Turn on a smart light.",
            arguments={
                "device": "Name or ID of the light device",
                "room": "Room containing the light",
            },
        )
    ]

    prompt = AICapabilityResolver._build_prompt(
        text="Turn on the living room light",
        definitions=definitions,
    )

    assert "Name: smart_home.light.turn_on" in prompt
    assert "Description: Turn on a smart light." in prompt
    assert (
        "- device: Name or ID of the light device"
        in prompt
    )
    assert "- room: Room containing the light" in prompt


def test_build_prompt_contains_safety_rules() -> None:
    definitions = [
        CapabilityDefinition(
            name="system.health",
            description="Check JarvisAI system health.",
        )
    ]

    prompt = AICapabilityResolver._build_prompt(
        text="Check the system",
        definitions=definitions,
    )

    assert "Never invent a capability." in prompt
    assert (
        "If no capability clearly matches, return null."
        in prompt
    )
    assert "Return JSON only." in prompt