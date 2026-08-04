from __future__ import annotations

from jarvis.services.capability import CapabilityDefinition
from jarvis.services.capability_registry import CapabilityRegistry
from jarvis.tools.safe import ReadOnlyToolDefinitionFactory


def make_factory() -> ReadOnlyToolDefinitionFactory:
    registry = CapabilityRegistry(
        [
            CapabilityDefinition(
                name="system.execution_anomalies",
                description=(
                    "Detect, prioritize, and summarize advisory "
                    "execution anomalies with safe operator "
                    "recommendations. Read-only."
                ),
            ),
            CapabilityDefinition(
                name="smart_home.turn_on",
                description="Turn on a smart-home device.",
                arguments={
                    "device_query": "Device query.",
                },
            ),
            CapabilityDefinition(
                name="smart_home.turn_off",
                description="Turn off a smart-home device.",
                arguments={
                    "device_query": "Device query.",
                },
            ),
            CapabilityDefinition(
                name="smart_home.toggle",
                description="Toggle a smart-home device.",
                arguments={
                    "device_query": "Device query.",
                },
            ),
        ]
    )

    return ReadOnlyToolDefinitionFactory(
        registry
    )


def test_execution_anomaly_tool_is_exposed_read_only() -> None:
    factory = make_factory()

    names = {
        definition.name
        for definition in factory.list_definitions()
    }

    assert (
        "system_execution_anomalies"
        in names
    )


def test_smart_home_side_effect_tools_remain_filtered() -> None:
    factory = make_factory()

    names = {
        definition.name
        for definition in factory.list_definitions()
    }

    assert "smart_home_turn_on" not in names
    assert "smart_home_turn_off" not in names
    assert "smart_home_toggle" not in names
