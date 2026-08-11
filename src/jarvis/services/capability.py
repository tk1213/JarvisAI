from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

CapabilityArgumentType = Literal[
    "string",
    "integer",
    "number",
    "boolean",
    "array",
    "object",
]


@dataclass(slots=True, frozen=True)
class CapabilityArgument:
    """Structured capability argument metadata.

    Existing capabilities may continue using plain strings for argument
    descriptions. Structured arguments opt in to richer JSON Schema output
    for native tool calling.
    """

    description: str = ""
    type: CapabilityArgumentType = "string"
    required: bool = False
    enum: tuple[Any, ...] = ()
    minimum: int | float | None = None
    maximum: int | float | None = None
    items_type: CapabilityArgumentType | None = None

    def __post_init__(self) -> None:
        description = self.description.strip()

        object.__setattr__(
            self,
            "description",
            description,
        )

        if (
            self.minimum is not None
            and self.maximum is not None
            and self.minimum > self.maximum
        ):
            raise ValueError(
                "CapabilityArgument minimum cannot exceed maximum."
            )

        if self.items_type is not None and self.type != "array":
            raise ValueError(
                "CapabilityArgument items_type is only valid for arrays."
            )

    def __str__(self) -> str:
        return self.description

    def to_json_schema(self) -> dict[str, Any]:
        schema: dict[str, Any] = {
            "type": self.type,
        }

        if self.description:
            schema["description"] = self.description

        if self.enum:
            schema["enum"] = list(self.enum)

        if self.minimum is not None:
            schema["minimum"] = self.minimum

        if self.maximum is not None:
            schema["maximum"] = self.maximum

        if self.type == "array" and self.items_type is not None:
            schema["items"] = {
                "type": self.items_type,
            }

        return schema


CapabilityArgumentDefinition = str | CapabilityArgument


@dataclass(slots=True, frozen=True)
class CapabilityDefinition:
    name: str
    description: str = ""
    arguments: dict[str, CapabilityArgumentDefinition] = field(
        default_factory=dict,
    )

    def __post_init__(self) -> None:
        name = self.name.strip()

        if not name:
            raise ValueError(
                "Capability name cannot be empty."
            )

        object.__setattr__(
            self,
            "name",
            name,
        )


@dataclass(slots=True, frozen=True)
class CapabilityRequest:
    capability: str
    arguments: dict[str, Any] = field(
        default_factory=dict,
    )

    def __post_init__(self) -> None:
        capability = self.capability.strip()

        if not capability:
            raise ValueError(
                "Capability cannot be empty."
            )

        object.__setattr__(
            self,
            "capability",
            capability,
        )
