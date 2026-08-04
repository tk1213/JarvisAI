from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True, frozen=True)
class CapabilityDefinition:
    name: str
    description: str = ""
    arguments: dict[str, str] = field(
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