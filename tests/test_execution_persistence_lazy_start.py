from __future__ import annotations

import asyncio

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

@pytest.mark.asyncio
async def test_concurrent_startup_initializes_repository_once() -> None:
    entered = asyncio.Event()
    release = asyncio.Event()

    class BlockingRepository(FakeRepository):
        async def startup(self) -> None:
            self.startup_calls += 1
            entered.set()
            await release.wait()

    repository = BlockingRepository()

    service = ExecutionPersistenceService(
        repository  # type: ignore[arg-type]
    )

    first = asyncio.create_task(
        service.startup()
    )

    await entered.wait()

    second = asyncio.create_task(
        service.startup()
    )

    await asyncio.sleep(0)

    release.set()

    await asyncio.gather(
        first,
        second,
    )

    assert repository.startup_calls == 1
    assert service.started is True

@pytest.mark.asyncio
async def test_startup_failure_leaves_service_not_started_and_allows_retry() -> None:
    class FailingOnceRepository(FakeRepository):
        def __init__(self) -> None:
            super().__init__()
            self.fail = True

        async def startup(self) -> None:
            self.startup_calls += 1

            if self.fail:
                self.fail = False
                raise RuntimeError(
                    "startup failed"
                )

    repository = FailingOnceRepository()

    service = ExecutionPersistenceService(
        repository  # type: ignore[arg-type]
    )

    with pytest.raises(
        RuntimeError,
        match="startup failed",
    ):
        await service.startup()

    assert service.started is False
    assert repository.startup_calls == 1

    await service.startup()

    assert service.started is True
    assert repository.startup_calls == 2

@pytest.mark.asyncio
async def test_cancelled_startup_leaves_service_retryable() -> None:
    entered = asyncio.Event()

    class BlockingRepository(FakeRepository):
        async def startup(self) -> None:
            self.startup_calls += 1
            entered.set()
            await asyncio.Future()

    repository = BlockingRepository()

    service = ExecutionPersistenceService(
        repository  # type: ignore[arg-type]
    )

    task = asyncio.create_task(
        service.startup()
    )

    await entered.wait()

    task.cancel()

    with pytest.raises(
        asyncio.CancelledError,
    ):
        await task

    assert service.started is False
    assert repository.startup_calls == 1

@pytest.mark.asyncio
async def test_cancelling_waiting_startup_does_not_cancel_active_startup() -> None:
    entered = asyncio.Event()
    release = asyncio.Event()

    class BlockingRepository(FakeRepository):
        async def startup(self) -> None:
            self.startup_calls += 1
            entered.set()
            await release.wait()

    repository = BlockingRepository()

    service = ExecutionPersistenceService(
        repository  # type: ignore[arg-type]
    )

    first = asyncio.create_task(
        service.startup()
    )

    await entered.wait()

    second = asyncio.create_task(
        service.startup()
    )

    await asyncio.sleep(0)

    second.cancel()

    with pytest.raises(
        asyncio.CancelledError,
    ):
        await second

    assert first.done() is False
    assert service.started is False

    release.set()

    await first

    assert service.started is True
    assert repository.startup_calls == 1

@pytest.mark.asyncio
async def test_cancelled_startup_releases_lock_and_allows_successful_retry() -> None:
    entered = asyncio.Event()
    allow_retry = asyncio.Event()

    class CancelThenSucceedRepository(FakeRepository):
        async def startup(self) -> None:
            self.startup_calls += 1

            if self.startup_calls == 1:
                entered.set()
                await asyncio.Future()

            await allow_retry.wait()

    repository = CancelThenSucceedRepository()

    service = ExecutionPersistenceService(
        repository  # type: ignore[arg-type]
    )

    first = asyncio.create_task(
        service.startup()
    )

    await entered.wait()

    first.cancel()

    with pytest.raises(
        asyncio.CancelledError
    ):
        await first

    assert service.started is False
    assert repository.startup_calls == 1

    second = asyncio.create_task(
        service.startup()
    )

    while repository.startup_calls < 2:
        await asyncio.sleep(0)

    assert second.done() is False

    allow_retry.set()

    await second

    assert service.started is True
    assert repository.startup_calls == 2