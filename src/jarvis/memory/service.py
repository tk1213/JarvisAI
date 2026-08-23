from __future__ import annotations

from datetime import UTC, datetime

from jarvis.core.logger import log
from jarvis.memory.audit import MemoryAuditAction
from jarvis.memory.audit_service import MemoryAuditService
from jarvis.memory.conflict import MemoryConflictPolicy
from jarvis.memory.models import Memory
from jarvis.memory.repository import MemoryRepository
from jarvis.memory.types import (
    MemoryCategory,
    MemoryImportance,
)


class MemoryService:
    def __init__(
        self,
        repository: MemoryRepository,
        *,
        audit: MemoryAuditService | None = None,
    ) -> None:
        self._repository = repository
        self._audit = audit
        self._last_audit_error: str | None = None

    @property
    def last_audit_error(
        self,
    ) -> str | None:
        return self._last_audit_error

    async def remember(
        self,
        *,
        category: MemoryCategory,
        key: str,
        value: str,
        importance: MemoryImportance = MemoryImportance.NORMAL,
        source: str = "user",
        conflict_policy: MemoryConflictPolicy = (
            MemoryConflictPolicy.REPLACE
        ),
    ) -> int:
        key = key.strip()
        value = value.strip()
        source = source.strip()

        if not key:
            raise ValueError(
                "Memory key cannot be empty."
            )

        if not value:
            raise ValueError(
                "Memory value cannot be empty."
            )

        if not source:
            raise ValueError(
                "Memory source cannot be empty."
            )

        existing = await self._repository.find_by_key(
            key
        )

        if existing:
            current = existing[0]

            if current.id is None:
                raise RuntimeError(
                    "Existing memory has no ID."
                )

            if (
                conflict_policy
                is MemoryConflictPolicy.KEEP_EXISTING
            ):
                await self._record_audit(
                    action=MemoryAuditAction.UNCHANGED,
                    key=key,
                    value=current.value,
                    source=source,
                    reason="keep_existing_policy",
                )

                return current.id

            if (
                current.category is category
                and current.value == value
                and current.importance is importance
                and current.source == source
            ):
                await self._record_audit(
                    action=MemoryAuditAction.UNCHANGED,
                    key=key,
                    value=value,
                    source=source,
                    reason="duplicate_memory",
                )

                return current.id

            updated = Memory(
                id=current.id,
                category=category,
                key=key,
                value=value,
                importance=importance,
                source=source,
                created_at=current.created_at,
                updated_at=datetime.now(UTC),
            )

            if not await self._repository.update(
                updated
            ):
                raise RuntimeError(
                    "Memory update failed."
                )

            await self._record_audit(
                action=MemoryAuditAction.UPDATED,
                key=key,
                value=value,
                source=source,
                reason="replace_policy",
            )

            return current.id

        now = datetime.now(UTC)

        memory_id = await self._repository.add(
            Memory(
                id=None,
                category=category,
                key=key,
                value=value,
                importance=importance,
                source=source,
                created_at=now,
                updated_at=now,
            )
        )

        await self._record_audit(
            action=MemoryAuditAction.CREATED,
            key=key,
            value=value,
            source=source,
            reason="new_memory",
        )

        return memory_id

    async def recall(
        self,
        key: str,
    ) -> Memory | None:
        key = key.strip()

        if not key:
            return None

        memories = await self._repository.find_by_key(
            key
        )

        return memories[0] if memories else None

    async def forget(
        self,
        key: str,
    ) -> bool:
        key = key.strip()

        if not key:
            return False

        deleted_any = False

        for memory in await self._repository.find_by_key(
            key
        ):
            if memory.id is None:
                continue

            deleted = await self._repository.delete(
                memory.id
            )

            if deleted:
                deleted_any = True

                await self._record_audit(
                    action=MemoryAuditAction.DELETED,
                    key=memory.key,
                    value=memory.value,
                    source="user",
                    reason="forget_key",
                )

        return deleted_any

    async def forget_category(
        self,
        category: MemoryCategory,
    ) -> int:
        deleted_count = 0

        for memory in await self._repository.find_by_category(
            category
        ):
            if memory.id is None:
                continue

            if await self._repository.delete(
                memory.id
            ):
                deleted_count += 1

                await self._record_audit(
                    action=MemoryAuditAction.DELETED,
                    key=memory.key,
                    value=memory.value,
                    source="user",
                    reason="forget_category",
                )

        return deleted_count

    async def forget_all(
        self,
    ) -> int:
        deleted_count = 0

        for memory in await self._repository.list_all():
            if memory.id is None:
                continue

            if await self._repository.delete(
                memory.id
            ):
                deleted_count += 1

                await self._record_audit(
                    action=MemoryAuditAction.DELETED,
                    key=memory.key,
                    value=memory.value,
                    source="user",
                    reason="forget_all",
                )

        return deleted_count

    async def list_memories(
        self,
        *,
        limit: int | None = None,
    ) -> list[Memory]:
        return await self._repository.list_all(
            limit=limit
        )

    async def find_category(
        self,
        category: MemoryCategory,
    ) -> list[Memory]:
        return await self._repository.find_by_category(
            category
        )

    async def _record_audit(
        self,
        *,
        action: MemoryAuditAction,
        key: str,
        value: str | None,
        source: str,
        reason: str,
    ) -> None:
        self._last_audit_error = None

        if self._audit is None:
            return

        try:
            await self._audit.record(
                action=action,
                key=key,
                value=value,
                source=source,
                reason=reason,
            )

        except Exception as exc:  # noqa: BLE001
            self._last_audit_error = str(
                exc
            )

            log.exception(
                "Memory audit failed after primary memory operation "
                "completed; preserving the completed memory outcome."
            )