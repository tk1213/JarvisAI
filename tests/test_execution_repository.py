from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
)

from jarvis.database.db import DatabaseManager
from jarvis.planner.execution_record import (
    ExecutionEventRecord,
    PlanExecutionRecord,
    StepExecutionRecord,
)
from jarvis.planner.execution_repository import (
    PlanExecutionRepository,
)


def make_record(
    *,
    goal: str = "Ping Jarvis",
) -> PlanExecutionRecord:
    return PlanExecutionRecord(
        goal=goal,
        plan_status="completed",
        success=True,
        completed_steps=1,
        steps=(
            StepExecutionRecord(
                step_index=1,
                capability="system.ping",
                status="completed",
                attempts=1,
                output={
                    "status": "ok",
                },
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


async def make_database(
    path: Path,
) -> DatabaseManager:
    database = DatabaseManager()

    await database.engine.dispose()

    database.engine = create_async_engine(
        f"sqlite+aiosqlite:///{path.as_posix()}",
        echo=False,
    )
    database.session_factory = async_sessionmaker(
        bind=database.engine,
        expire_on_commit=False,
    )

    return database


@pytest.mark.asyncio
async def test_repository_saves_and_loads_record(
    tmp_path: Path,
) -> None:
    database = await make_database(
        tmp_path / "records.db"
    )

    try:
        repository = PlanExecutionRepository(
            database
        )

        await repository.startup()

        record_id = await repository.save(
            make_record()
        )

        loaded = await repository.get(
            record_id
        )

        assert record_id >= 1
        assert loaded is not None
        assert loaded.goal == "Ping Jarvis"
        assert loaded.success is True
        assert (
            loaded.steps[0].capability
            == "system.ping"
        )
        assert (
            loaded.events[0].event_type
            == "plan_started"
        )

    finally:
        await database.engine.dispose()


@pytest.mark.asyncio
async def test_repository_lists_recent_records(
    tmp_path: Path,
) -> None:
    database = await make_database(
        tmp_path / "recent.db"
    )

    try:
        repository = PlanExecutionRepository(
            database
        )

        await repository.startup()

        await repository.save(
            make_record(
                goal="First"
            )
        )
        await repository.save(
            make_record(
                goal="Second"
            )
        )

        records = await repository.list_recent(
            limit=2
        )

        assert [
            record.goal
            for record in records
        ] == [
            "Second",
            "First",
        ]

    finally:
        await database.engine.dispose()
