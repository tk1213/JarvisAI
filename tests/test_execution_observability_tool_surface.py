from __future__ import annotations

from jarvis.services.capability import CapabilityDefinition
from jarvis.services.capability_registry import CapabilityRegistry
from jarvis.tools.definitions import ToolDefinitionFactory


def make_factory() -> ToolDefinitionFactory:
    registry = CapabilityRegistry(
        [
            CapabilityDefinition(
                name="system.execution_detail",
                description=(
                    "Show detailed information for one "
                    "persisted planner execution. Read-only."
                ),
                arguments={
                    "record_id": (
                        "Execution record ID as a positive integer."
                    ),
                },
            ),
            CapabilityDefinition(
                name="system.execution_diagnostics",
                description=(
                    "Diagnose failures, retries, and timeouts "
                    "for one persisted planner execution. "
                    "Read-only."
                ),
                arguments={
                    "record_id": (
                        "Execution record ID as a positive integer."
                    ),
                },
            ),
        ]
    )

    return ToolDefinitionFactory(
        registry
    )


def test_execution_observability_tools_have_native_names() -> None:
    factory = make_factory()

    definitions = {
        definition.name: definition
        for definition in factory.list_definitions()
    }

    assert set(
        definitions
    ) == {
        "system_execution_detail",
        "system_execution_diagnostics",
    }

    assert (
        factory.resolve_capability_name(
            "system_execution_detail"
        )
        == "system.execution_detail"
    )

    assert (
        factory.resolve_capability_name(
            "system_execution_diagnostics"
        )
        == "system.execution_diagnostics"
    )


def test_execution_observability_tools_require_record_id() -> None:
    factory = make_factory()

    definitions = {
        definition.name: definition
        for definition in factory.list_definitions()
    }

    expected_parameters = {
        "type": "object",
        "properties": {
            "record_id": {
                "type": "string",
                "description": (
                    "Execution record ID as a positive integer."
                ),
            },
        },
        "additionalProperties": False,
    }

    assert (
        definitions[
            "system_execution_detail"
        ].parameters
        == expected_parameters
    )

    assert (
        definitions[
            "system_execution_diagnostics"
        ].parameters
        == expected_parameters
    )


def test_openai_tool_payloads_are_valid_function_tools() -> None:
    factory = make_factory()

    tools = factory.to_openai_tools()

    assert len(
        tools
    ) == 2

    names = {
        tool["name"]
        for tool in tools
    }

    assert names == {
        "system_execution_detail",
        "system_execution_diagnostics",
    }

    for tool in tools:
        assert tool["type"] == "function"
        assert (
            tool["parameters"][
                "additionalProperties"
            ]
            is False
        )
