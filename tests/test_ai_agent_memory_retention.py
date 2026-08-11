from __future__ import annotations

import pytest

from jarvis.agent.memory_retention import AIAgentMemoryRetentionPolicy


class Repository:
    def __init__(
        self,
        *,
        count: int,
        deleted: int = 0,
    ) -> None:
        self.total = count
        self.deleted = deleted
        self.keep_calls = []

    async def count(
        self,
    ) -> int:
        return self.total

    async def delete_oldest(
        self,
        *,
        keep: int,
    ) -> int:
        self.keep_calls.append(
            keep
        )
        return self.deleted


@pytest.mark.asyncio
async def test_retention_skips_cleanup_within_limit() -> None:
    repository = Repository(
        count=5
    )

    result = await AIAgentMemoryRetentionPolicy(
        repository,  # type: ignore[arg-type]
        max_records=10,
    ).enforce()

    assert result.before == 5
    assert result.deleted == 0
    assert result.after == 5
    assert repository.keep_calls == []


@pytest.mark.asyncio
async def test_retention_deletes_oldest_overflow() -> None:
    repository = Repository(
        count=12,
        deleted=2,
    )

    result = await AIAgentMemoryRetentionPolicy(
        repository,  # type: ignore[arg-type]
        max_records=10,
    ).enforce()

    assert repository.keep_calls == [
        10
    ]
    assert result.before == 12
    assert result.deleted == 2
    assert result.after == 10


def test_retention_rejects_invalid_limit() -> None:
    with pytest.raises(
        ValueError,
        match="max_records",
    ):
        AIAgentMemoryRetentionPolicy(
            Repository(count=0),  # type: ignore[arg-type]
            max_records=0,
        )
