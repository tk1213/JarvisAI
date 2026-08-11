from __future__ import annotations

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
