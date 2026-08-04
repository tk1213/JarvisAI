from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from jarvis.services.capability import CapabilityDefinition
from jarvis.skills.metadata import SkillMetadata


class Skill(ABC):
    def __init__(self) -> None:
        self.enabled = True

    @property
    @abstractmethod
    def metadata(self) -> SkillMetadata:
        ...

    @property
    def capability_definitions(
        self,
    ) -> list[CapabilityDefinition]:
        return [
            CapabilityDefinition(
                name=capability,
            )
            for capability in self.metadata.capabilities
        ]

    async def startup(self) -> None:
        """Called when Jarvis starts."""

    async def shutdown(self) -> None:
        """Called when Jarvis stops."""

    async def health(self) -> dict[str, Any]:
        return {
            "healthy": True,
        }

    @abstractmethod
    async def execute(
        self,
        command: str,
        **kwargs: Any,
    ) -> Any:
        """Execute the skill."""