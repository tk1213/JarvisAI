from __future__ import annotations

import pytest

from jarvis.agent.memory_repository import AIAgentMemoryRepository


def test_delete_oldest_rejects_negative_keep() -> None:
    repository = object.__new__(
        AIAgentMemoryRepository
    )

    with pytest.raises(
        ValueError,
        match="keep",
    ):
        # Validation occurs before database access.
        import asyncio

        asyncio.run(
            repository.delete_oldest(
                keep=-1
            )
        )
