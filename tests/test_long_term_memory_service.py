from __future__ import annotations

from datetime import UTC, datetime

import pytest

from jarvis.memory.conflict import MemoryConflictPolicy
from jarvis.memory.models import Memory
from jarvis.memory.service import MemoryService
from jarvis.memory.types import MemoryCategory, MemoryImportance


class StubRepository:
    def __init__(self) -> None:
        self.memories: list[Memory] = []
        self.update_calls = 0
        self.next_id = 1

    async def add(self, memory: Memory) -> int:
        memory_id = self.next_id
        self.next_id += 1
        self.memories.append(
            Memory(
                id=memory_id,
                category=memory.category,
                key=memory.key,
                value=memory.value,
                importance=memory.importance,
                source=memory.source,
                created_at=memory.created_at,
                updated_at=memory.updated_at,
            )
        )
        return memory_id

    async def update(self, memory: Memory) -> bool:
        self.update_calls += 1
        for index, item in enumerate(self.memories):
            if item.id == memory.id:
                self.memories[index] = memory
                return True
        return False

    async def delete(self, memory_id: int) -> bool:
        before = len(self.memories)
        self.memories = [m for m in self.memories if m.id != memory_id]
        return len(self.memories) < before

    async def find_by_key(self, key: str) -> list[Memory]:
        return [m for m in self.memories if m.key == key]

    async def find_by_category(
        self,
        category: MemoryCategory,
    ) -> list[Memory]:
        return [m for m in self.memories if m.category is category]

    async def list_all(
        self,
        *,
        limit: int | None = None,
    ) -> list[Memory]:
        return self.memories if limit is None else self.memories[:limit]


def service_pair() -> tuple[MemoryService, StubRepository]:
    repo = StubRepository()
    return MemoryService(repo), repo  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_replace_policy_updates_conflict() -> None:
    service, repo = service_pair()

    await service.remember(
        category=MemoryCategory.PERSONAL,
        key="user_name",
        value="Old",
    )

    await service.remember(
        category=MemoryCategory.PERSONAL,
        key="user_name",
        value="TK",
        conflict_policy=MemoryConflictPolicy.REPLACE,
    )

    assert repo.memories[0].value == "TK"
    assert repo.update_calls == 1


@pytest.mark.asyncio
async def test_keep_existing_policy_preserves_value() -> None:
    service, repo = service_pair()

    await service.remember(
        category=MemoryCategory.PERSONAL,
        key="user_name",
        value="TK",
    )

    await service.remember(
        category=MemoryCategory.PERSONAL,
        key="user_name",
        value="Other",
        conflict_policy=MemoryConflictPolicy.KEEP_EXISTING,
    )

    assert repo.memories[0].value == "TK"
    assert repo.update_calls == 0


@pytest.mark.asyncio
async def test_same_memory_does_not_update() -> None:
    service, repo = service_pair()

    await service.remember(
        category=MemoryCategory.PERSONAL,
        key="user_name",
        value="TK",
    )

    await service.remember(
        category=MemoryCategory.PERSONAL,
        key="user_name",
        value="TK",
    )

    assert repo.update_calls == 0


@pytest.mark.asyncio
async def test_forget_category_and_all() -> None:
    service, repo = service_pair()
    now = datetime.now(UTC)

    repo.memories = [
        Memory(
            id=1,
            category=MemoryCategory.PERSONAL,
            key="user_name",
            value="TK",
            importance=MemoryImportance.HIGH,
            source="test",
            created_at=now,
            updated_at=now,
        ),
        Memory(
            id=2,
            category=MemoryCategory.PREFERENCE,
            key="favorite_drink",
            value="coffee",
            importance=MemoryImportance.NORMAL,
            source="test",
            created_at=now,
            updated_at=now,
        ),
    ]

    assert await service.forget_category(MemoryCategory.PREFERENCE) == 1
    assert [m.key for m in repo.memories] == ["user_name"]
    assert await service.forget_all() == 1
    assert repo.memories == []
