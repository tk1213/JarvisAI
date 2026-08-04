from __future__ import annotations

from datetime import UTC, datetime

import pytest

from jarvis.memory.commands import MemoryCommandService
from jarvis.memory.extractor import MemoryExtractor
from jarvis.memory.models import Memory
from jarvis.memory.types import (
    MemoryCategory,
    MemoryImportance,
)


class StubMemoryService:
    def __init__(self) -> None:
        self.memories: dict[str, Memory] = {}

    async def remember(
        self,
        *,
        category: MemoryCategory,
        key: str,
        value: str,
        importance: MemoryImportance = MemoryImportance.NORMAL,
        source: str = "user",
        **kwargs: object,
    ) -> int:
        del kwargs
        now = datetime.now(UTC)

        self.memories[key] = Memory(
            id=1,
            category=category,
            key=key,
            value=value,
            importance=importance,
            source=source,
            created_at=now,
            updated_at=now,
        )

        return 1

    async def recall(
        self,
        key: str,
    ) -> Memory | None:
        return self.memories.get(
            key
        )

    async def list_memories(
        self,
        *,
        limit: int | None = None,
    ) -> list[Memory]:
        values = list(
            self.memories.values()
        )

        if limit is None:
            return values

        return values[:limit]

    async def forget(
        self,
        key: str,
    ) -> bool:
        return self.memories.pop(
            key,
            None,
        ) is not None

    async def forget_all(
        self,
    ) -> int:
        count = len(
            self.memories
        )
        self.memories.clear()
        return count


def build_service() -> tuple[
    MemoryCommandService,
    StubMemoryService,
]:
    memory = StubMemoryService()
    service = MemoryCommandService(
        memory=memory,  # type: ignore[arg-type]
        extractor=MemoryExtractor(),
    )

    return service, memory


@pytest.mark.asyncio
async def test_remember_command_stores_fact() -> None:
    commands, memory = build_service()

    reply = await commands.handle(
        "Remember that my name is TK"
    )

    assert reply is not None
    assert memory.memories["user_name"].value == "TK"
    assert memory.memories["user_name"].source == "user"


@pytest.mark.asyncio
async def test_list_memories() -> None:
    commands, memory = build_service()

    await memory.remember(
        category=MemoryCategory.PERSONAL,
        key="user_name",
        value="TK",
        importance=MemoryImportance.HIGH,
    )

    reply = await commands.handle(
        "What do you remember about me?"
    )

    assert reply is not None
    assert "TK" in reply
    assert "user_name" not in reply


@pytest.mark.asyncio
async def test_forget_requires_confirmation() -> None:
    commands, memory = build_service()

    await memory.remember(
        category=MemoryCategory.PERSONAL,
        key="user_name",
        value="TK",
    )

    first = await commands.handle(
        "Forget my name"
    )

    assert first is not None
    assert commands.has_pending_confirmation is True
    assert "user_name" in memory.memories

    second = await commands.handle(
        "confirm"
    )

    assert second is not None
    assert "user_name" not in memory.memories
    assert commands.has_pending_confirmation is False


@pytest.mark.asyncio
async def test_delete_can_be_cancelled() -> None:
    commands, memory = build_service()

    await memory.remember(
        category=MemoryCategory.PERSONAL,
        key="user_name",
        value="TK",
    )

    await commands.handle(
        "Forget my name"
    )

    reply = await commands.handle(
        "cancel"
    )

    assert reply == "Memory deletion cancelled."
    assert "user_name" in memory.memories


@pytest.mark.asyncio
async def test_forget_all_requires_confirmation() -> None:
    commands, memory = build_service()

    await memory.remember(
        category=MemoryCategory.PERSONAL,
        key="user_name",
        value="TK",
    )

    await commands.handle(
        "Forget everything about me"
    )

    assert len(memory.memories) == 1

    reply = await commands.handle(
        "confirm"
    )

    assert reply == "Deleted 1 long-term memories."
    assert memory.memories == [] or memory.memories == {}
