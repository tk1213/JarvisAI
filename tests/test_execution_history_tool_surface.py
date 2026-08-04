from __future__ import annotations

from jarvis.services.capability import CapabilityDefinition
from jarvis.services.capability_registry import CapabilityRegistry
from jarvis.tools.definitions import ToolDefinitionFactory


def test_execution_history_is_exposed_as_read_only_tool() -> None:
    registry = CapabilityRegistry(
        [
            CapabilityDefinition(
                name="system.execution_history",
                description=(
                    "Show recent JarvisAI planner execution "
                    "history. This is read-only."
                ),
            )
        ]
    )

    factory = ToolDefinitionFactory(
        registry
    )

    definitions = factory.list_definitions()

    assert len(definitions) == 1

    definition = definitions[0]

    assert (
        definition.name
        == "system_execution_history"
    )

    assert (
        factory.resolve_capability_name(
            definition.name
        )
        == "system.execution_history"
    )

    assert (
        definition.parameters
        == {
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        }
    )