from __future__ import annotations

from datetime import UTC, datetime

import pytest

from jarvis.core.container import container
from jarvis.planner.execution_persistence import (
    ExecutionPersistenceService,
)
from jarvis.planner.execution_record import (
    ExecutionEventRecord,
    PlanExecutionRecord,
    StepExecutionRecord,
)
from jarvis.skills.builtin.system_skill import SystemSkill


class DummyContext:
    pass


class FakeRepository:
    async def startup(self) -> None:
        pass

    async def save(
        self,
        record: PlanExecutionRecord,
    ) -> int:
        del record
        return 1

    async def get(
        self,
        record_id: int,
    ) -> PlanExecutionRecord | None:
        del record_id
        return None

    async def list_recent(
        self,
        *,
        limit: int = 100,
    ) -> list[PlanExecutionRecord]:
        del limit

        return [
            PlanExecutionRecord(
                goal="Healthy ping",
                plan_status="completed",
                success=True,
                completed_steps=1,
                steps=(
                    StepExecutionRecord(
                        step_index=1,
                        capability="system.ping",
                        status="completed",
                        attempts=1,
                    ),
                ),
                events=(
                    ExecutionEventRecord(
                        sequence=1,
                        event_type="plan_started",
                        timestamp=datetime.now(UTC),
                        step_index=None,
                        capability=None,
                        attempt=None,
                        details={},
                    ),
                ),
            )
        ]


def install_persistence() -> dict[str, object]:
    existing = dict(
        container._services  # type: ignore[attr-defined]
    )

    container.clear()

    persistence = ExecutionPersistenceService(
        FakeRepository()  # type: ignore[arg-type]
    )

    container.register(
        "execution_persistence",
        persistence,
    )

    return existing


def restore_container(
    existing: dict[str, object],
) -> None:
    container.clear()

    for name, service in existing.items():
        container.register(
            name,
            service,
        )


def test_execution_analytics_capabilities_are_declared() -> None:
    skill = SystemSkill(
        DummyContext()  # type: ignore[arg-type]
    )

    names = {
        definition.name
        for definition in skill.capability_definitions
    }

    assert {
        "system.execution_statistics",
        "system.capability_reliability",
        "system.execution_health",
        "system.execution_health_trend",
    }.issubset(
        names
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "capability",
    [
        "system.execution_statistics",
        "system.capability_reliability",
        "system.execution_health",
        "system.execution_health_trend",
    ],
)
async def test_execution_analytics_capabilities_return_read_only_data(
    capability: str,
) -> None:
    existing = install_persistence()

    try:
        skill = SystemSkill(
            DummyContext()  # type: ignore[arg-type]
        )

        result = await skill.execute(
            capability
        )

        assert result["available"] is True
        assert result["summary"]

    finally:
        restore_container(
            existing
        )
