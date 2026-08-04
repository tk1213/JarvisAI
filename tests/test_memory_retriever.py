from __future__ import annotations

from datetime import UTC, datetime

import pytest

from jarvis.memory.models import Memory
from jarvis.memory.retriever import MemoryRetriever
from jarvis.memory.types import (
    MemoryCategory,
    MemoryImportance,
)


class StubMemoryService:
    def __init__(
        self,
        memories: list[Memory],
    ) -> None:
        self._memories = memories

    async def list_memories(
        self,
        *,
        limit: int | None = None,
    ) -> list[Memory]:
        if limit is None:
            return self._memories

        return self._memories[:limit]


def make_memory(
    *,
    memory_id: int,
    category: MemoryCategory,
    key: str,
    value: str,
    importance: MemoryImportance = MemoryImportance.NORMAL,
) -> Memory:
    now = datetime.now(UTC)

    return Memory(
        id=memory_id,
        category=category,
        key=key,
        value=value,
        importance=importance,
        source="test",
        created_at=now,
        updated_at=now,
    )


@pytest.mark.asyncio
async def test_retrieve_user_name() -> None:
    service = StubMemoryService(
        [
            make_memory(
                memory_id=1,
                category=MemoryCategory.PERSONAL,
                key="user_name",
                value="TK",
                importance=MemoryImportance.HIGH,
            ),
            make_memory(
                memory_id=2,
                category=MemoryCategory.PREFERENCE,
                key="favorite_drink",
                value="black coffee",
            ),
        ]
    )

    retriever = MemoryRetriever(
        service,  # type: ignore[arg-type]
    )

    results = await retriever.retrieve(
        "What is my name?"
    )

    assert len(results) == 1
    assert results[0].key == "user_name"
    assert results[0].value == "TK"


@pytest.mark.asyncio
async def test_retrieve_favorite_drink() -> None:
    service = StubMemoryService(
        [
            make_memory(
                memory_id=1,
                category=MemoryCategory.PERSONAL,
                key="user_name",
                value="TK",
            ),
            make_memory(
                memory_id=2,
                category=MemoryCategory.PREFERENCE,
                key="favorite_drink",
                value="black coffee",
            ),
        ]
    )

    retriever = MemoryRetriever(
        service,  # type: ignore[arg-type]
    )

    results = await retriever.retrieve(
        "What is my favorite drink?"
    )

    assert len(results) == 1
    assert results[0].key == "favorite_drink"


@pytest.mark.asyncio
async def test_irrelevant_query_returns_no_memories() -> None:
    service = StubMemoryService(
        [
            make_memory(
                memory_id=1,
                category=MemoryCategory.PERSONAL,
                key="user_name",
                value="TK",
            )
        ]
    )

    retriever = MemoryRetriever(
        service,  # type: ignore[arg-type]
    )

    results = await retriever.retrieve(
        "What is the weather today?"
    )

    assert results == []


@pytest.mark.asyncio
async def test_thai_name_query_matches_user_name() -> None:
    service = StubMemoryService(
        [
            make_memory(
                memory_id=1,
                category=MemoryCategory.PERSONAL,
                key="user_name",
                value="TK",
            )
        ]
    )

    retriever = MemoryRetriever(
        service,  # type: ignore[arg-type]
    )

    results = await retriever.retrieve(
        "ผมชื่ออะไร"
    )

    assert len(results) == 1
    assert results[0].key == "user_name"


@pytest.mark.asyncio
async def test_limit_is_applied() -> None:
    service = StubMemoryService(
        [
            make_memory(
                memory_id=1,
                category=MemoryCategory.PERSONAL,
                key="user_name",
                value="TK",
            ),
            make_memory(
                memory_id=2,
                category=MemoryCategory.FAMILY,
                key="daughter_name",
                value="Diana",
            ),
        ]
    )

    retriever = MemoryRetriever(
        service,  # type: ignore[arg-type]
    )

    results = await retriever.retrieve(
        "Tell me my name and my daughter name",
        limit=1,
    )

    assert len(results) == 1


def test_invalid_candidate_limit() -> None:
    service = StubMemoryService(
        []
    )

    with pytest.raises(
        ValueError,
        match="candidate_limit",
    ):
        MemoryRetriever(
            service,  # type: ignore[arg-type]
            candidate_limit=0,
        )
