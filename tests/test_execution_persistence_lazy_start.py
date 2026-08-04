from __future__ import annotations

import pytest

from jarvis.planner.execution_persistence import (
    ExecutionPersistenceService,
)
from jarvis.planner.execution_record import (
    PlanExecutionRecord,
)


class FakeRepository:
    def __init__(self) -> None:
        self.startup_calls = 0

    async def startup(self) -> None:
        self.startup_calls += 1

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
        limit: int = 20,
    ) -> list[PlanExecutionRecord]:
        del limit
        return []


@pytest.mark.asyncio
async def test_startup_is_idempotent() -> None:
    repository = FakeRepository()

    service = ExecutionPersistenceService(
        repository  # type: ignore[arg-type]
    )

    await service.startup()
    await service.startup()

    assert repository.startup_calls == 1
    assert service.started is True


@pytest.mark.asyncio
async def test_read_path_lazily_starts_repository() -> None:
    repository = FakeRepository()

    service = ExecutionPersistenceService(
        repository  # type: ignore[arg-type]
    )

    await service.list_recent()

    assert repository.startup_calls == 1
    assert service.started is True
