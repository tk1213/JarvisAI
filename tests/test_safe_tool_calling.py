from __future__ import annotations

from typing import Any

import pytest

from jarvis.services.capability import CapabilityDefinition
from jarvis.services.capability_registry import CapabilityRegistry
from jarvis.tools.contracts import ToolCall
from jarvis.tools.safe import ReadOnlyToolDefinitionFactory, ReadOnlyToolExecutor


class StubRouter:
    def __init__(self) -> None:
        self.calls: list[str] = []

    async def execute_request(
        self,
        request,
    ) -> Any:
        self.calls.append(request.capability)
        return {"ok": True}


def make_registry() -> CapabilityRegistry:
    return CapabilityRegistry(
        [
            CapabilityDefinition(
                name="smart_home.status",
                description="Read status.",
                arguments={"device_query": "Device description"},
            ),
            CapabilityDefinition(
                name="smart_home.toggle",
                description="Toggle device.",
                arguments={"device_query": "Device description"},
            ),
            CapabilityDefinition(
                name="smart_home.turn_off",
                description="Turn off device.",
                arguments={"device_query": "Device description"},
            ),
            CapabilityDefinition(
                name="system.ping",
                description="Ping Jarvis.",
            ),
        ]
    )


def test_read_only_definition_factory_filters_side_effects() -> None:
    factory = ReadOnlyToolDefinitionFactory(make_registry())

    names = [
        definition.name
        for definition in factory.list_definitions()
    ]

    assert names == [
        "smart_home_status",
        "system_ping",
    ]


@pytest.mark.asyncio
async def test_read_only_executor_blocks_turn_off() -> None:
    registry = make_registry()
    router = StubRouter()

    executor = ReadOnlyToolExecutor(
        registry=registry,
        router=router,  # type: ignore[arg-type]
    )

    result = await executor.execute(
        ToolCall(
            name="smart_home.turn_off",
            arguments={"device_query": "Smart Plug 1"},
        )
    )

    assert result.success is False
    assert result.error is not None
    assert result.error.code == "tool_requires_confirmation"
    assert router.calls == []


@pytest.mark.asyncio
async def test_read_only_executor_blocks_toggle() -> None:
    registry = make_registry()
    router = StubRouter()

    executor = ReadOnlyToolExecutor(
        registry=registry,
        router=router,  # type: ignore[arg-type]
    )

    result = await executor.execute(
        ToolCall(
            name="smart_home.toggle",
            arguments={"device_query": "Smart Plug 1"},
        )
    )

    assert result.success is False
    assert result.error is not None
    assert result.error.code == "tool_requires_confirmation"
    assert router.calls == []


@pytest.mark.asyncio
async def test_read_only_executor_allows_status() -> None:
    registry = make_registry()
    router = StubRouter()

    executor = ReadOnlyToolExecutor(
        registry=registry,
        router=router,  # type: ignore[arg-type]
    )

    result = await executor.execute(
        ToolCall(
            name="smart_home.status",
            arguments={"device_query": "Smart Plug 1"},
        )
    )

    assert result.success is True
    assert router.calls == ["smart_home.status"]
