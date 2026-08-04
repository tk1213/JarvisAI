from __future__ import annotations

from jarvis.services.capability import CapabilityDefinition
from jarvis.services.capability_registry import CapabilityRegistry
from jarvis.tools.safe import ReadOnlyToolDefinitionFactory


def make_factory() -> ReadOnlyToolDefinitionFactory:
    registry = CapabilityRegistry(
        [
            CapabilityDefinition(
                name="system.execution_statistics",
                description="Read execution statistics.",
            ),
            CapabilityDefinition(
                name="system.capability_reliability",
                description="Read capability reliability.",
            ),
            CapabilityDefinition(
                name="system.execution_health",
                description="Read execution health.",
            ),
            CapabilityDefinition(
                name="system.execution_health_trend",
                description="Read execution health trend.",
            ),
            CapabilityDefinition(
                name="smart_home.turn_on",
                description="Turn on a smart-home device.",
                arguments={
                    "device_query": "Device query.",
                },
            ),
        ]
    )

    return ReadOnlyToolDefinitionFactory(
        registry
    )


def test_analytics_tools_are_exposed_on_read_only_surface() -> None:
    factory = make_factory()

    names = {
        definition.name
        for definition in factory.list_definitions()
    }

    assert names == {
        "system_capability_reliability",
        "system_execution_health",
        "system_execution_health_trend",
        "system_execution_statistics",
    }


def test_side_effect_tool_is_not_exposed() -> None:
    factory = make_factory()

    names = {
        definition.name
        for definition in factory.list_definitions()
    }

    assert (
        "smart_home_turn_on"
        not in names
    )
