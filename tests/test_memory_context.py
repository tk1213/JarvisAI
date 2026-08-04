from __future__ import annotations

from datetime import UTC, datetime

import pytest

from jarvis.memory.context import MemoryContextBuilder
from jarvis.memory.models import Memory
from jarvis.memory.types import (
    MemoryCategory,
    MemoryImportance,
)


class StubRetriever:
    def __init__(
        self,
        memories: list[Memory],
    ) -> None:
        self._memories = memories
        self.calls: list[tuple[str, int]] = []

    async def retrieve(
        self,
        query: str,
        *,
        limit: int = 8,
    ) -> list[Memory]:
        self.calls.append(
            (
                query,
                limit,
            )
        )

        return self._memories[:limit]


def make_memory() -> Memory:
    now = datetime.now(UTC)

    return Memory(
        id=1,
        category=MemoryCategory.PERSONAL,
        key="user_name",
        value="TK",
        importance=MemoryImportance.HIGH,
        source="test",
        created_at=now,
        updated_at=now,
    )


@pytest.mark.asyncio
async def test_context_contains_relevant_memory() -> None:
    retriever = StubRetriever(
        [make_memory()]
    )

    builder = MemoryContextBuilder(
        retriever,  # type: ignore[arg-type]
    )

    context = await builder.build(
        "What is my name?"
    )

    assert "user_name = TK" in context
    assert retriever.calls == [
        (
            "What is my name?",
            8,
        )
    ]


@pytest.mark.asyncio
async def test_context_empty_without_relevant_memory() -> None:
    retriever = StubRetriever(
        []
    )

    builder = MemoryContextBuilder(
        retriever,  # type: ignore[arg-type]
    )

    context = await builder.build(
        "What is the weather?"
    )

    assert context == ""


def test_invalid_context_limit() -> None:
    retriever = StubRetriever(
        []
    )

    with pytest.raises(
        ValueError,
        match="max_memories",
    ):
        MemoryContextBuilder(
            retriever,  # type: ignore[arg-type]
            max_memories=0,
        )
