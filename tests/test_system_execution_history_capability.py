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

    async def list_recent(
        self,
        *,
        limit: int = 20,
    ) -> list[PlanExecutionRecord]:
        assert limit == 10

        return [
            PlanExecutionRecord(
                goal="Ping Jarvis",
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

    async def get(
        self,
        record_id: int,
    ) -> PlanExecutionRecord | None:
        del record_id
        return None

    async def save(
        self,
        record: PlanExecutionRecord,
    ) -> int:
        del record
        return 1


@pytest.mark.asyncio
async def test_execution_history_capability_is_declared() -> None:
    skill = SystemSkill(
        DummyContext()  # type: ignore[arg-type]
    )

    assert (
        "system.execution_history"
        in skill.metadata.capabilities
    )

    definitions = {
        definition.name: definition
        for definition in skill.capability_definitions
    }

    assert (
        "system.execution_history"
        in definitions
    )


@pytest.mark.asyncio
async def test_execution_history_capability_returns_report() -> None:
    existing = dict(
        container._services  # type: ignore[attr-defined]
    )

    try:
        container.clear()

        persistence = ExecutionPersistenceService(
            FakeRepository()  # type: ignore[arg-type]
        )

        container.register(
            "execution_persistence",
            persistence,
        )

        skill = SystemSkill(
            DummyContext()  # type: ignore[arg-type]
        )

        result = await skill.execute(
            "system.execution_history"
        )

        assert result["available"] is True
        assert result["total"] == 1
        assert result["completed"] == 1
        assert result["failed"] == 0
        assert (
            "Ping Jarvis [completed]"
            in result["records"][0]
        )

    finally:
        container.clear()

        for name, service in existing.items():
            container.register(
                name,
                service,
            )


@pytest.mark.asyncio
async def test_execution_history_unavailable_without_persistence() -> None:
    existing = dict(
        container._services  # type: ignore[attr-defined]
    )

    try:
        container.clear()

        skill = SystemSkill(
            DummyContext()  # type: ignore[arg-type]
        )

        result = await skill.execute(
            "system.execution_history"
        )

        assert result == {
            "available": False,
            "summary": (
                "Execution history is not available."
            ),
            "records": [],
        }

    finally:
        container.clear()

        for name, service in existing.items():
            container.register(
                name,
                service,
            )