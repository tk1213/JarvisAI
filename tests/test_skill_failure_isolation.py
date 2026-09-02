from __future__ import annotations

import asyncio
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


class BrokenShutdownSkill(GoodSkill):
    async def shutdown(self) -> None:
        self._events.append(
            f"stop:{self._name}"
        )

        raise RuntimeError(
            "shutdown exploded"
        )

class CancelledShutdownSkill(GoodSkill):
    async def shutdown(self) -> None:
        self._events.append(
            f"stop:{self._name}"
        )

        raise asyncio.CancelledError()

class FailingShutdownSkill(GoodSkill):
    async def shutdown(self) -> None:
        self._events.append(
            f"stop:{self._name}"
        )

        raise RuntimeError(
            "shutdown failed"
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


@pytest.mark.asyncio
async def test_shutdown_failure_does_not_block_other_started_skills() -> None:
    events: list[str] = []

    manager = SkillManager()

    manager.register(
        GoodSkill(
            "first",
            events,
        )
    )
    manager.register(
        BrokenShutdownSkill(
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
        "stop:broken",
    ]

    assert manager.list_started_skills() == []

@pytest.mark.asyncio
async def test_shutdown_finishes_remaining_skills_before_propagating_cancellation() -> None:
    events: list[str] = []

    manager = SkillManager()

    manager.register(
        GoodSkill(
            "first",
            events,
        )
    )
    manager.register(
        CancelledShutdownSkill(
            "cancelled",
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

    with pytest.raises(
        asyncio.CancelledError
    ):
        await manager.shutdown()

    assert events == [
        "start:cancelled",
        "start:first",
        "start:last",
        "stop:last",
        "stop:first",
        "stop:cancelled",
    ]

    assert manager.list_started_skills() == []

@pytest.mark.asyncio
async def test_shutdown_preserves_cancellation_when_later_skill_fails() -> None:
    events: list[str] = []

    manager = SkillManager()

    manager.register(
        FailingShutdownSkill(
            "alpha",
            events,
        )
    )
    manager.register(
        CancelledShutdownSkill(
            "beta",
            events,
        )
    )
    manager.register(
        GoodSkill(
            "gamma",
            events,
        )
    )

    await manager.startup()

    with pytest.raises(
        asyncio.CancelledError
    ):
        await manager.shutdown()

    assert events == [
        "start:alpha",
        "start:beta",
        "start:gamma",
        "stop:gamma",
        "stop:beta",
        "stop:alpha",
    ]

    assert manager.list_started_skills() == []