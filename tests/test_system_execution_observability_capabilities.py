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
        if record_id != 7:
            return None

        return PlanExecutionRecord(
            goal="Inspect execution",
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

    async def list_recent(
        self,
        *,
        limit: int = 20,
    ) -> list[PlanExecutionRecord]:
        del limit
        return []


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


def test_new_observability_capabilities_are_declared() -> None:
    skill = SystemSkill(
        DummyContext()  # type: ignore[arg-type]
    )

    names = {
        definition.name
        for definition in skill.capability_definitions
    }

    assert (
        "system.execution_detail"
        in names
    )
    assert (
        "system.execution_diagnostics"
        in names
    )


@pytest.mark.asyncio
async def test_execution_detail_capability_returns_detail() -> None:
    existing = install_persistence()

    try:
        skill = SystemSkill(
            DummyContext()  # type: ignore[arg-type]
        )

        result = await skill.execute(
            "system.execution_detail",
            record_id="7",
        )

        assert result["available"] is True
        assert result["record_id"] == 7
        assert result["status"] == "failed"
        assert result["failure_count"] == 1
        assert (
            "system.health [failed]"
            in result["steps"][0]
        )

    finally:
        restore_container(
            existing
        )


@pytest.mark.asyncio
async def test_execution_diagnostics_capability_returns_findings() -> None:
    existing = install_persistence()

    try:
        skill = SystemSkill(
            DummyContext()  # type: ignore[arg-type]
        )

        result = await skill.execute(
            "system.execution_diagnostics",
            record_id=7,
        )

        assert result["available"] is True
        assert result["record_id"] == 7
        assert result["failed_steps"] == [
            "system.health",
        ]
        assert result["retry_steps"] == [
            "system.health",
        ]
        assert result["timeout_steps"] == [
            "system.health",
        ]

    finally:
        restore_container(
            existing
        )


@pytest.mark.asyncio
async def test_execution_detail_returns_not_found() -> None:
    existing = install_persistence()

    try:
        skill = SystemSkill(
            DummyContext()  # type: ignore[arg-type]
        )

        result = await skill.execute(
            "system.execution_detail",
            record_id=99,
        )

        assert result["available"] is False
        assert (
            result["summary"]
            == "Execution record 99 was not found."
        )

    finally:
        restore_container(
            existing
        )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "value",
    [
        None,
        "",
        "abc",
        "0",
        -1,
    ],
)
async def test_execution_record_id_validation(
    value: object,
) -> None:
    skill = SystemSkill(
        DummyContext()  # type: ignore[arg-type]
    )

    kwargs = {}

    if value is not None:
        kwargs[
            "record_id"
        ] = value

    with pytest.raises(
        ValueError,
        match="record_id",
    ):
        await skill.execute(
            "system.execution_detail",
            **kwargs,
        )
