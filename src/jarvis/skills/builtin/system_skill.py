from __future__ import annotations

from typing import Any

from jarvis.services.capability import CapabilityDefinition
from jarvis.skills.base import Skill
from jarvis.skills.context import SkillContext
from jarvis.skills.metadata import SkillMetadata
from jarvis.version import __version__


class SystemSkill(Skill):
    def __init__(
        self,
        context: SkillContext,
    ) -> None:
        super().__init__()
        self.context = context

    @property
    def metadata(self) -> SkillMetadata:
        return SkillMetadata(
            name="system",
            version="1.0.0",
            description="Built-in system utilities",
            capabilities=[
                "system.ping",
                "system.health",
                "system.version",
            ],
            priority=1,
        )

    @property
    def capability_definitions(
        self,
    ) -> list[CapabilityDefinition]:
        return [
            CapabilityDefinition(
                name="system.ping",
                description=(
                    "Check whether JarvisAI is running "
                    "and responding."
                ),
            ),
            CapabilityDefinition(
                name="system.health",
                description=(
                    "Check the current health status "
                    "of JarvisAI."
                ),
            ),
            CapabilityDefinition(
                name="system.version",
                description=(
                    "Get the current JarvisAI version."
                ),
            ),
        ]

    async def startup(self) -> None:
        pass

    async def shutdown(self) -> None:
        pass

    async def execute(
        self,
        command: str,
        **kwargs: Any,
    ) -> Any:
        if command == "system.ping":
            return {
                "status": "ok",
            }

        if command == "system.version":
            return {
                 "jarvis": __version__,
        }

        if command == "system.health":
            return await self.health()

        raise ValueError(
            f"Unsupported command: {command}"
        )

    async def health(self) -> dict[str, Any]:
        return {
            "healthy": True,
            "skill": self.metadata.name,
            "version": self.metadata.version,
        }