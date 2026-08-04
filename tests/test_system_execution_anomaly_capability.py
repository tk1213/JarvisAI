from __future__ import annotations

from datetime import UTC, datetime

import pytest

from jarvis.core.container import container
from jarvis.planner.execution_persistence import ExecutionPersistenceService
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

    async def save(self, record: PlanExecutionRecord) -> int:
        del record
        return 1

    async def get(self, record_id: int) -> PlanExecutionRecord | None:
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
                goal="Failed health",
                plan_status="failed",
                success=False,
                completed_steps=0,
                steps=(
                    StepExecutionRecord(
                        step_index=1,
                        capability="system.health",
                        status="failed",
                        attempts=2,
                        error="capability execution timed out",
                    ),
                ),
                events=(
                    ExecutionEventRecord(
                        sequence=1,
                        event_type="step_failed",
                        timestamp=datetime.now(UTC),
                        step_index=1,
                        capability="system.health",
                        attempt=2,
                        details={
                            "error": "capability execution timed out",
                        },
                    ),
                ),
            )
        ]


def install_persistence() -> dict[str, object]:
    existing = dict(
        container._services  # type: ignore[attr-defined]
    )

    container.clear()
    container.register(
        "execution_persistence",
        ExecutionPersistenceService(
            FakeRepository()  # type: ignore[arg-type]
        ),
    )
    return existing


def restore_container(existing: dict[str, object]) -> None:
    container.clear()

    for name, service in existing.items():
        container.register(name, service)


def test_execution_anomaly_capability_is_declared() -> None:
    skill = SystemSkill(
        DummyContext()  # type: ignore[arg-type]
    )

    names = {
        definition.name
        for definition in skill.capability_definitions
    }

    assert "system.execution_anomalies" in names


@pytest.mark.asyncio
async def test_execution_anomaly_capability_returns_reports() -> None:
    existing = install_persistence()

    try:
        skill = SystemSkill(
            DummyContext()  # type: ignore[arg-type]
        )

        result = await skill.execute(
            "system.execution_anomalies"
        )

        assert result["available"] is True
        assert result["total"] >= 1
        assert result["anomalies"]
        assert result["triage"]
        assert result["advice"]

    finally:
        restore_container(existing)
