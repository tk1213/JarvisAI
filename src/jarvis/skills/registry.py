from __future__ import annotations

from collections.abc import Iterator

from jarvis.skills.base import Skill


class SkillRegistry:
    def __init__(self) -> None:
        self._skills: dict[str, Skill] = {}

    def register(
        self,
        skill: Skill,
        *,
        overwrite: bool = False,
    ) -> None:
        name = skill.metadata.name

        if not overwrite and name in self._skills:
            raise ValueError(
                f"Skill '{name}' is already registered."
            )

        self._skills[name] = skill

    def unregister(self, name: str) -> None:
        self._skills.pop(name, None)

    def get(self, name: str) -> Skill:
        try:
            return self._skills[name]
        except KeyError as exc:
            raise KeyError(
                f"Skill '{name}' is not registered."
            ) from exc

    def has(self, name: str) -> bool:
        return name in self._skills

    def list(self) -> list[Skill]:
        return sorted(
            self._skills.values(),
            key=lambda skill: skill.metadata.name,
        )

    def names(self) -> list[str]:
        return sorted(self._skills.keys())

    def capabilities(self) -> dict[str, list[Skill]]:
        result: dict[str, list[Skill]] = {}

        for skill in self._skills.values():
            for capability in skill.metadata.capabilities:
                result.setdefault(
                    capability,
                    [],
                ).append(skill)

        return result

    def find_by_capability(
        self,
        capability: str,
    ) -> list[Skill]:
        return [
            skill
            for skill in self._skills.values()
            if capability in skill.metadata.capabilities
        ]

    def clear(self) -> None:
        self._skills.clear()

    def __contains__(self, name: str) -> bool:
        return self.has(name)

    def __len__(self) -> int:
        return len(self._skills)

    def __iter__(self) -> Iterator[Skill]:
        return iter(self.list())