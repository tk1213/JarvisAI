from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

import pytest

from jarvis.memory.audit import MemoryAuditAction
from jarvis.memory.models import Memory
from jarvis.memory.service import MemoryService
from jarvis.memory.types import (
    MemoryCategory,
    MemoryImportance,
)


@dataclass
class StubAudit:
    calls: list[dict[str, object]] = field(
        default_factory=list
    )

    async def record(
        self,
        **kwargs: object,
    ) -> None:
        self.calls.append(
            kwargs
        )


class StubRepository:
    def __init__(self) -> None:
        self.memory: Memory | None = None

    async def find_by_key(
        self,
        key: str,
    ) -> list[Memory]:
        if self.memory is None:
            return []

        if self.memory.key != key:
            return []

        return [
            self.memory
        ]

    async def add(
        self,
        memory: Memory,
    ) -> int:
        self.memory = Memory(
            id=1,
            category=memory.category,
            key=memory.key,
            value=memory.value,
            importance=memory.importance,
            source=memory.source,
            created_at=memory.created_at,
            updated_at=memory.updated_at,
        )
        return 1

    async def update(
        self,
        memory: Memory,
    ) -> bool:
        self.memory = memory
        return True

    async def delete(
        self,
        memory_id: int,
    ) -> bool:
        if (
            self.memory is None
            or self.memory.id != memory_id
        ):
            return False

        self.memory = None
        return True

    async def find_by_category(
        self,
        category: MemoryCategory,
    ) -> list[Memory]:
        if (
            self.memory is not None
            and self.memory.category is category
        ):
            return [
                self.memory
            ]

        return []

    async def list_all(
        self,
        *,
        limit: int | None = None,
    ) -> list[Memory]:
        del limit

        return (
            []
            if self.memory is None
            else [
                self.memory
            ]
        )


@pytest.mark.asyncio
async def test_created_memory_is_audited() -> None:
    repository = StubRepository()
    audit = StubAudit()

    service = MemoryService(
        repository,  # type: ignore[arg-type]
        audit=audit,  # type: ignore[arg-type]
    )

    await service.remember(
        category=MemoryCategory.PERSONAL,
        key="user_name",
        value="TK",
        importance=MemoryImportance.HIGH,
        source="user",
    )

    assert audit.calls[0]["action"] is MemoryAuditAction.CREATED


@pytest.mark.asyncio
async def test_deleted_memory_is_audited() -> None:
    now = datetime.now(UTC)
    repository = StubRepository()
    repository.memory = Memory(
        id=1,
        category=MemoryCategory.PERSONAL,
        key="user_name",
        value="TK",
        importance=MemoryImportance.HIGH,
        source="user",
        created_at=now,
        updated_at=now,
    )
    audit = StubAudit()

    service = MemoryService(
        repository,  # type: ignore[arg-type]
        audit=audit,  # type: ignore[arg-type]
    )

    deleted = await service.forget(
        "user_name"
    )

    assert deleted is True
    assert audit.calls[0]["action"] is MemoryAuditAction.DELETED
