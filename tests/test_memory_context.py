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



@pytest.mark.asyncio
async def test_context_treats_memory_as_reference_data() -> None:
    retriever = StubRetriever(
        [make_memory()]
    )

    builder = MemoryContextBuilder(
        retriever,  # type: ignore[arg-type]
    )

    context = await builder.build(
        "What is my name?"
    )

    assert "reference data" in context
    assert "not as instructions" in context


@pytest.mark.asyncio
async def test_context_normalizes_multiline_memory_values() -> None:
    now = datetime.now(UTC)

    memory = Memory(
        id=2,
        category=MemoryCategory.PREFERENCE,
        key="note",
        value="line one\nline two\r\nline three",
        importance=MemoryImportance.NORMAL,
        source="test",
        created_at=now,
        updated_at=now,
    )

    builder = MemoryContextBuilder(
        StubRetriever([memory]),  # type: ignore[arg-type]
    )

    context = await builder.build(
        "note"
    )

    assert "line one line two line three" in context


@pytest.mark.asyncio
async def test_context_deduplicates_identical_memories() -> None:
    memory = make_memory()

    builder = MemoryContextBuilder(
        StubRetriever(  # type: ignore[arg-type]
            [
                memory,
                memory,
            ]
        ),
    )

    context = await builder.build(
        "What is my name?"
    )

    assert context.count("user_name = TK") == 1


@pytest.mark.asyncio
async def test_context_respects_character_budget() -> None:
    now = datetime.now(UTC)

    memory = Memory(
        id=3,
        category=MemoryCategory.PREFERENCE,
        key="long_note",
        value="x" * 1000,
        importance=MemoryImportance.NORMAL,
        source="test",
        created_at=now,
        updated_at=now,
    )

    builder = MemoryContextBuilder(
        StubRetriever([memory]),  # type: ignore[arg-type]
        max_context_chars=512,
        max_value_chars=64,
    )

    context = await builder.build(
        "long note"
    )

    assert len(context) <= 512
    assert "…" in context


def test_invalid_context_character_budget() -> None:
    with pytest.raises(
        ValueError,
        match="max_context_chars",
    ):
        MemoryContextBuilder(
            StubRetriever([]),  # type: ignore[arg-type]
            max_context_chars=255,
        )


def test_invalid_memory_value_limit() -> None:
    with pytest.raises(
        ValueError,
        match="max_value_chars",
    ):
        MemoryContextBuilder(
            StubRetriever([]),  # type: ignore[arg-type]
            max_value_chars=31,
        )
