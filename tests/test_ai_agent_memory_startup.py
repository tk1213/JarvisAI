from __future__ import annotations

import asyncio

import pytest

from jarvis.agent.memory_startup import AIAgentMemoryStartupService


class FakeLifecycle:
    def __init__(
        self,
        restored: int,
    ) -> None:
        self.restored = restored
        self.calls = 0

    async def restore_durable_memory(
        self,
    ) -> int:
        self.calls += 1
        return self.restored


@pytest.mark.asyncio
async def test_startup_service_restores_once() -> None:
    lifecycle = FakeLifecycle(
        restored=3
    )

    service = AIAgentMemoryStartupService(
        lifecycle,  # type: ignore[arg-type]
    )

    first = await service.restore()
    second = await service.restore()

    assert first == 3
    assert second == 3
    assert lifecycle.calls == 1
    assert service.restored is True
    assert service.restored_records == 3


@pytest.mark.asyncio
async def test_startup_service_handles_empty_restore() -> None:
    lifecycle = FakeLifecycle(
        restored=0
    )

    service = AIAgentMemoryStartupService(
        lifecycle,  # type: ignore[arg-type]
    )

    restored = await service.restore()

    assert restored == 0
    assert service.restored is True
    assert service.restored_records == 0

@pytest.mark.asyncio
async def test_concurrent_restore_runs_lifecycle_once() -> None:
    entered = asyncio.Event()
    release = asyncio.Event()

    class BlockingLifecycle:
        def __init__(self) -> None:
            self.calls = 0

        async def restore_durable_memory(
            self,
        ) -> int:
            self.calls += 1
            entered.set()

            await release.wait()

            return 3

    lifecycle = BlockingLifecycle()

    service = AIAgentMemoryStartupService(
        lifecycle,  # type: ignore[arg-type]
    )

    first = asyncio.create_task(
        service.restore()
    )

    await entered.wait()

    second = asyncio.create_task(
        service.restore()
    )

    await asyncio.sleep(0)

    release.set()

    first_result, second_result = await asyncio.gather(
        first,
        second,
    )

    assert first_result == 3
    assert second_result == 3

    assert lifecycle.calls == 1
    assert service.restored is True
    assert service.restored_records == 3

@pytest.mark.asyncio
async def test_cancelled_restore_leaves_service_retryable() -> None:
    entered = asyncio.Event()

    class BlockingLifecycle:
        def __init__(self) -> None:
            self.calls = 0

        async def restore_durable_memory(
            self,
        ) -> int:
            self.calls += 1
            entered.set()
            await asyncio.Future()
            return 3

    lifecycle = BlockingLifecycle()

    service = AIAgentMemoryStartupService(
        lifecycle,  # type: ignore[arg-type]
    )

    task = asyncio.create_task(
        service.restore()
    )

    await entered.wait()

    task.cancel()

    with pytest.raises(
        asyncio.CancelledError,
    ):
        await task

    assert service.restored is False
    assert service.restored_records == 0
    assert lifecycle.calls == 1

@pytest.mark.asyncio
async def test_cancelling_waiting_restore_does_not_cancel_active_restore() -> None:
    entered = asyncio.Event()
    release = asyncio.Event()

    class BlockingLifecycle:
        def __init__(self) -> None:
            self.calls = 0

        async def restore_durable_memory(
            self,
        ) -> int:
            self.calls += 1
            entered.set()
            await release.wait()
            return 3

    lifecycle = BlockingLifecycle()

    service = AIAgentMemoryStartupService(
        lifecycle,  # type: ignore[arg-type]
    )

    first = asyncio.create_task(
        service.restore()
    )

    await entered.wait()

    second = asyncio.create_task(
        service.restore()
    )

    await asyncio.sleep(0)

    second.cancel()

    with pytest.raises(
        asyncio.CancelledError,
    ):
        await second

    assert first.done() is False
    assert service.restored is False

    release.set()

    result = await first

    assert result == 3
    assert lifecycle.calls == 1
    assert service.restored is True
    assert service.restored_records == 3

@pytest.mark.asyncio
async def test_retention_failure_does_not_block_durable_restore() -> None:
    class FailingRetention:
        async def enforce(
            self,
        ):
            raise RuntimeError(
                "retention failed"
            )

    lifecycle = FakeLifecycle(
        restored=3
    )

    service = AIAgentMemoryStartupService(
        lifecycle,  # type: ignore[arg-type]
        retention=FailingRetention(),  # type: ignore[arg-type]
    )

    restored = await service.restore()

    assert restored == 3
    assert lifecycle.calls == 1
    assert service.restored is True
    assert service.restored_records == 3
    assert service.retention_result is None
    assert service.retention_error == "retention failed"

@pytest.mark.asyncio
async def test_retention_cancellation_propagates_and_does_not_restore() -> None:
    class CancellingRetention:
        async def enforce(
            self,
        ):
            raise asyncio.CancelledError

    lifecycle = FakeLifecycle(
        restored=3
    )

    service = AIAgentMemoryStartupService(
        lifecycle,  # type: ignore[arg-type]
        retention=CancellingRetention(),  # type: ignore[arg-type]
    )

    with pytest.raises(
        asyncio.CancelledError,
    ):
        await service.restore()

    assert lifecycle.calls == 0
    assert service.restored is False
    assert service.restored_records == 0
    assert service.retention_result is None
    assert service.retention_error is None

@pytest.mark.asyncio
async def test_retention_failure_does_not_block_durable_restore() -> None:
    class FailingRetention:
        async def enforce(
            self,
        ):
            raise RuntimeError(
                "retention failed"
            )

    lifecycle = FakeLifecycle(
        restored=3
    )

    service = AIAgentMemoryStartupService(
        lifecycle,  # type: ignore[arg-type]
        retention=FailingRetention(),  # type: ignore[arg-type]
    )

    restored = await service.restore()

    assert restored == 3
    assert lifecycle.calls == 1
    assert service.restored is True
    assert service.restored_records == 3
    assert service.retention_result is None
    assert service.retention_error == "retention failed"

@pytest.mark.asyncio
async def test_retention_cancellation_propagates_and_does_not_restore() -> None:
    class CancellingRetention:
        async def enforce(
            self,
        ):
            raise asyncio.CancelledError

    lifecycle = FakeLifecycle(
        restored=3
    )

    service = AIAgentMemoryStartupService(
        lifecycle,  # type: ignore[arg-type]
        retention=CancellingRetention(),  # type: ignore[arg-type]
    )

    with pytest.raises(
        asyncio.CancelledError,
    ):
        await service.restore()

    assert lifecycle.calls == 0
    assert service.restored is False
    assert service.restored_records == 0
    assert service.retention_result is None
    assert service.retention_error is None

@pytest.mark.asyncio
async def test_restore_failure_after_retention_success_remains_retryable() -> None:
    class Retention:
        def __init__(self) -> None:
            self.calls = 0

        async def enforce(
            self,
        ):
            self.calls += 1

            return object()

    class FailingOnceLifecycle:
        def __init__(self) -> None:
            self.calls = 0

        async def restore_durable_memory(
            self,
        ) -> int:
            self.calls += 1

            if self.calls == 1:
                raise RuntimeError(
                    "restore failed"
                )

            return 3

    lifecycle = FailingOnceLifecycle()
    retention = Retention()

    service = AIAgentMemoryStartupService(
        lifecycle,  # type: ignore[arg-type]
        retention=retention,  # type: ignore[arg-type]
    )

    with pytest.raises(
        RuntimeError,
        match="restore failed",
    ):
        await service.restore()

    assert service.restored is False
    assert service.restored_records == 0
    assert service.retention_result is not None
    assert service.retention_error is None

    restored = await service.restore()

    assert restored == 3
    assert service.restored is True
    assert service.restored_records == 3

    assert lifecycle.calls == 2
    assert retention.calls == 2
