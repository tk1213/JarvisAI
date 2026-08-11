from __future__ import annotations

from jarvis.services.capability import (
    CapabilityArgument,
    CapabilityDefinition,
)
from jarvis.services.capability_registry import CapabilityRegistry
from jarvis.tools.definitions import ToolDefinitionFactory


def main() -> None:
    registry = CapabilityRegistry(
        [
            CapabilityDefinition(
                name="system.execution_history",
                description="Read recent execution history.",
                arguments={
                    "limit": CapabilityArgument(
                        description="Maximum number of records.",
                        type="integer",
                        required=True,
                        minimum=1,
                        maximum=100,
                    ),
                    "include_failures": CapabilityArgument(
                        description="Include failed executions.",
                        type="boolean",
                    ),
                },
            ),
            CapabilityDefinition(
                name="system.ping",
                arguments={
                    "legacy": "Legacy string argument",
                },
            ),
        ]
    )

    tools = ToolDefinitionFactory(
        registry
    ).to_openai_tools()

    structured = tools[0]["parameters"]
    legacy = tools[1]["parameters"]

    assert structured["required"] == ["limit"]
    assert (
        structured["properties"]["limit"]["type"]
        == "integer"
    )
    assert (
        structured["properties"]["include_failures"]["type"]
        == "boolean"
    )
    assert (
        legacy["properties"]["legacy"]["type"]
        == "string"
    )

    print("Sprint 4.2 Pack A — Structured Tool Arguments")
    print("-" * 60)
    print("Structured schema: PASS")
    print("Legacy compatibility: PASS")
    print("Sprint 4.2 Pack A live gate: PASS")


if __name__ == "__main__":
    main()
