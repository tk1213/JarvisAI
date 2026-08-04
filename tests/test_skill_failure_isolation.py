from __future__ import annotations

from typing import Any

import pytest

from jarvis.services.capability import CapabilityDefinition
from jarvis.skills.base import Skill
from jarvis.skills.manager import SkillManager
from jarvis.skills.metadata import SkillMetadata


class GoodSkill(Skill):
    def __init__(
        self,
        name: str,
        events: list[str],
    ) -> None:
        super().__init__()

        self._name = name
        self._events = events

    @property
    def metadata(self) -> SkillMetadata:
        return SkillMetadata(
            name=self._name,
            version="1.0.0",
            description=f"{self._name} test skill",
            capabilities=[
                f"{self._name}.test",
            ],
        )

    @property
    def capability_definitions(
        self,
    ) -> list[CapabilityDefinition]:
        return [
            CapabilityDefinition(
                name=f"{self._name}.test",
                description="Test capability.",
            )
        ]

    async def startup(self) -> None:
        self._events.append(
            f"start:{self._name}"
        )

    async def shutdown(self) -> None:
        self._events.append(
            f"stop:{self._name}"
        )

    async def execute(
        self,
        command: str,
        **kwargs: Any,
    ) -> Any:
        return {
            "command": command,
        }


class BrokenSkill(GoodSkill):
    async def startup(self) -> None:
        self._events.append(
            f"start:{self._name}"
        )

        raise RuntimeError(
            "startup exploded"
        )


@pytest.mark.asyncio
async def test_broken_skill_does_not_stop_other_skills() -> None:
    events: list[str] = []

    manager = SkillManager()

    manager.register(
        GoodSkill(
            "first",
            events,
        )
    )
    manager.register(
        BrokenSkill(
            "broken",
            events,
        )
    )
    manager.register(
        GoodSkill(
            "last",
            events,
        )
    )

    await manager.startup()

    assert set(events) == {
        "start:first",
        "start:broken",
        "start:last",
    }

    assert manager.list_started_skills() == [
        "first",
        "last",
    ]

    assert manager.is_degraded is True

    assert manager.startup_errors() == {
        "broken": "startup exploded",
    }


@pytest.mark.asyncio
async def test_failed_skill_is_disabled() -> None:
    events: list[str] = []

    manager = SkillManager()

    broken = BrokenSkill(
        "broken",
        events,
    )

    manager.register(broken)

    await manager.startup()

    assert broken.enabled is False
    assert manager.is_degraded is True


@pytest.mark.asyncio
async def test_shutdown_only_stops_started_skills_in_reverse_order() -> None:
    events: list[str] = []

    manager = SkillManager()

    manager.register(
        GoodSkill(
            "first",
            events,
        )
    )
    manager.register(
        BrokenSkill(
            "broken",
            events,
        )
    )
    manager.register(
        GoodSkill(
            "last",
            events,
        )
    )

    await manager.startup()
    await manager.shutdown()

    assert events == [
        "start:broken",
        "start:first",
        "start:last",
        "stop:last",
        "stop:first",
    ]

    assert manager.list_started_skills() == []


@pytest.mark.asyncio
async def test_failed_skill_health_is_reported() -> None:
    events: list[str] = []

    manager = SkillManager()

    manager.register(
        BrokenSkill(
            "broken",
            events,
        )
    )

    await manager.startup()

    health = await manager.health()

    assert health["broken"]["healthy"] is False
    assert health["broken"]["enabled"] is False
    assert health["broken"]["error"] == "startup exploded"