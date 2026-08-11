from __future__ import annotations

import pytest

from jarvis.agent.memory_startup import AIAgentMemoryStartupService


class FakeLifecycle:
    def __init__(self) -> None:
        self.database_ready = False

    async def restore_durable_memory(
        self,
    ) -> int:
        if not self.database_ready:
            raise RuntimeError(
                "database is not ready"
            )

        return 2


@pytest.mark.asyncio
async def test_restore_requires_database_ready_ordering() -> None:
    lifecycle = FakeLifecycle()

    service = AIAgentMemoryStartupService(
        lifecycle,  # type: ignore[arg-type]
    )

    with pytest.raises(
        RuntimeError,
        match="database is not ready",
    ):
        await service.restore()

    lifecycle.database_ready = True

    restored = await service.restore()

    assert restored == 2
