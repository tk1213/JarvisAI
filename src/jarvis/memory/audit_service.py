from __future__ import annotations

from datetime import UTC, datetime

from jarvis.memory.audit import (
    MemoryAuditAction,
    MemoryAuditEvent,
)
from jarvis.memory.audit_repository import (
    MemoryAuditRepository,
)


class MemoryAuditService:
    def __init__(
        self,
        repository: MemoryAuditRepository,
    ) -> None:
        self._repository = repository

    async def record(
        self,
        *,
        action: MemoryAuditAction,
        key: str,
        value: str | None,
        source: str,
        reason: str,
    ) -> None:
        await self._repository.append(
            MemoryAuditEvent(
                action=action,
                key=key,
                value=value,
                source=source,
                reason=reason,
                created_at=datetime.now(UTC),
            )
        )

    async def list_recent(
        self,
        *,
        limit: int = 50,
    ) -> list[MemoryAuditEvent]:
        return await self._repository.list_recent(
            limit=limit
        )
