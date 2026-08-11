from jarvis.services.capability import CapabilityDefinition
from jarvis.services.capability_registry import CapabilityRegistry
from jarvis.tools.definitions import (
    ToolDefinition,
    ToolDefinitionFactory,
)


def test_tool_definition_to_openai_tool() -> None:
    definition = ToolDefinition(
        name="system_ping",
        description="Ping Jarvis.",
        parameters={
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        },
    )

    result = definition.to_openai_tool()

    assert result == {
        "type": "function",
        "name": "system_ping",
        "description": "Ping Jarvis.",
        "parameters": {
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        },
    }


def test_factory_serializes_capability_definition() -> None:
    registry = CapabilityRegistry(
        [
            CapabilityDefinition(
                name="smart_home.status",
                description="Read device status.",
                arguments={
                    "device": "Device name",
                },
            )
        ]
    )

    factory = ToolDefinitionFactory(
        registry
    )

    tools = factory.to_openai_tools()

    assert tools == [
        {
            "type": "function",
            "name": "smart_home_status",
            "description": "Read device status.",
            "parameters": {
                "type": "object",
                "properties": {
                    "device": {
                        "type": "string",
                        "description": "Device name",
                    }
                },
                "additionalProperties": False,
            },
        }
    ]


def test_factory_preserves_registry_order() -> None:
    registry = CapabilityRegistry(
        [
            CapabilityDefinition(
                name="system.version",
            ),
            CapabilityDefinition(
                name="system.ping",
            ),
        ]
    )

    factory = ToolDefinitionFactory(
        registry
    )

    names = [
        tool.name
        for tool in factory.list_definitions()
    ]

    assert names == [
        "system_ping",
        "system_version",
    ]


def test_missing_description_gets_fallback() -> None:
    definition = CapabilityDefinition(
        name="system.ping",
    )

    tool = ToolDefinitionFactory.from_capability_definition(
        definition
    )

    assert tool.description == "Execute capability system.ping"


def test_tool_name_mapping_round_trip() -> None:
    registry = CapabilityRegistry(
        [
            CapabilityDefinition(
                name="smart_home.turn_off",
            )
        ]
    )

    factory = ToolDefinitionFactory(
        registry
    )

    assert (
        factory.to_tool_name(
            "smart_home.turn_off"
        )
        == "smart_home_turn_off"
    )

    assert (
        factory.resolve_capability_name(
            "smart_home_turn_off"
        )
        == "smart_home.turn_off"
    )



def test_factory_serializes_structured_arguments() -> None:
    from jarvis.services.capability import CapabilityArgument

    registry = CapabilityRegistry(
        [
            CapabilityDefinition(
                name="system.execution_history",
                description="Read execution history.",
                arguments={
                    "limit": CapabilityArgument(
                        description="Maximum records",
                        type="integer",
                        required=True,
                        minimum=1,
                        maximum=100,
                    ),
                    "include_failures": CapabilityArgument(
                        description="Include failed executions",
                        type="boolean",
                    ),
                },
            )
        ]
    )

    tools = ToolDefinitionFactory(
        registry
    ).to_openai_tools()

    assert tools == [
        {
            "type": "function",
            "name": "system_execution_history",
            "description": "Read execution history.",
            "parameters": {
                "type": "object",
                "properties": {
                    "include_failures": {
                        "type": "boolean",
                        "description": "Include failed executions",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum records",
                        "minimum": 1,
                        "maximum": 100,
                    },
                },
                "additionalProperties": False,
                "required": ["limit"],
            },
        }
    ]
