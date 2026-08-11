from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from jarvis.services.capability import (
    CapabilityArgument,
    CapabilityArgumentDefinition,
    CapabilityDefinition,
)
from jarvis.services.capability_registry import CapabilityRegistry


@dataclass(slots=True, frozen=True)
class ToolDefinition:
    name: str
    description: str
    parameters: dict[str, Any]

    def __post_init__(self) -> None:
        normalized_name = self.name.strip()
        normalized_description = self.description.strip()

        if not normalized_name:
            raise ValueError(
                "ToolDefinition name cannot be empty."
            )

        object.__setattr__(
            self,
            "name",
            normalized_name,
        )
        object.__setattr__(
            self,
            "description",
            normalized_description,
        )

    def to_openai_tool(self) -> dict[str, Any]:
        return {
            "type": "function",
            "name": self.name,
            "description": self.description,
            "parameters": dict(
                self.parameters
            ),
        }


class ToolDefinitionFactory:
    def __init__(
        self,
        registry: CapabilityRegistry,
    ) -> None:
        self._registry = registry

    def list_definitions(
        self,
    ) -> list[ToolDefinition]:
        return [
            self.from_capability_definition(
                definition
            )
            for definition
            in self._registry.list_definitions()
        ]

    @staticmethod
    def from_capability_definition(
        definition: CapabilityDefinition,
    ) -> ToolDefinition:
        properties: dict[str, Any] = {}
        required: list[str] = []

        for name, argument in sorted(
            definition.arguments.items()
        ):
            properties[name] = (
                ToolDefinitionFactory._argument_schema(
                    argument
                )
            )

            if (
                isinstance(argument, CapabilityArgument)
                and argument.required
            ):
                required.append(name)

        parameters: dict[str, Any] = {
            "type": "object",
            "properties": properties,
            "additionalProperties": False,
        }

        if required:
            parameters["required"] = required

        return ToolDefinition(
            name=ToolDefinitionFactory.to_tool_name(
                definition.name
            ),
            description=(
                definition.description
                or (
                    "Execute capability "
                    f"{definition.name}"
                )
            ),
            parameters=parameters,
        )

    @staticmethod
    def _argument_schema(
        argument: CapabilityArgumentDefinition,
    ) -> dict[str, Any]:
        if isinstance(argument, CapabilityArgument):
            return argument.to_json_schema()

        return {
            "type": "string",
            "description": argument,
        }

    def to_openai_tools(
        self,
    ) -> list[dict[str, Any]]:
        return [
            definition.to_openai_tool()
            for definition in self.list_definitions()
        ]

    @staticmethod
    def to_tool_name(
        capability_name: str,
    ) -> str:
        return capability_name.replace(
            ".",
            "_",
        )

    def resolve_capability_name(
        self,
        tool_name: str,
    ) -> str | None:
        normalized = tool_name.strip()

        for capability_name in (
            self._registry.list_capabilities()
        ):
            if (
                self.to_tool_name(
                    capability_name
                )
                == normalized
            ):
                return capability_name

        return None
