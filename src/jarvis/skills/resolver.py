from __future__ import annotations

from jarvis.skills.base import Skill
from jarvis.skills.registry import SkillRegistry


class SkillResolver:
    def __init__(self, registry: SkillRegistry) -> None:
        self._registry = registry

    def resolve(self, capability: str) -> Skill | None:
        """
        Return the highest-priority enabled skill
        supporting the requested capability.
        """
        candidates = [
            skill
            for skill in self._registry.find_by_capability(capability)
            if skill.enabled and skill.metadata.enabled
        ]

        if not candidates:
            return None

        candidates.sort(
            key=lambda skill: skill.metadata.priority,
        )

        return candidates[0]

    def resolve_all(self, capability: str) -> list[Skill]:
        """
        Return all enabled skills sorted by priority.
        """
        candidates = [
            skill
            for skill in self._registry.find_by_capability(capability)
            if skill.enabled and skill.metadata.enabled
        ]

        candidates.sort(
            key=lambda skill: skill.metadata.priority,
        )

        return candidates