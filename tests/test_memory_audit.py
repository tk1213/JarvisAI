from __future__ import annotations

from dataclasses import dataclass, field

import pytest

from jarvis.memory.audit import (
    MemoryAuditAction,
    MemoryAuditEvent,
)
from jarvis.memory.audit_service import MemoryAuditService


@dataclass
class StubAuditRepository:
    events: list[MemoryAuditEvent] = field(
        default_factory=list
    )

    async def append(
        self,
        event: MemoryAuditEvent,
    ) -> None:
        self.events.append(
            event
        )

    async def list_recent(
        self,
        *,
        limit: int = 50,
    ) -> list[MemoryAuditEvent]:
        return self.events[-limit:]


@pytest.mark.asyncio
async def test_audit_service_records_event() -> None:
    repository = StubAuditRepository()

    audit = MemoryAuditService(
        repository,  # type: ignore[arg-type]
    )

    await audit.record(
        action=MemoryAuditAction.CREATED,
        key="user_name",
        value="TK",
        source="user",
        reason="new_memory",
    )

    assert len(repository.events) == 1
    assert repository.events[0].key == "user_name"
    assert repository.events[0].value == "TK"
    assert (
        repository.events[0].action
        is MemoryAuditAction.CREATED
    )


@pytest.mark.asyncio
async def test_audit_service_lists_events() -> None:
    repository = StubAuditRepository()

    audit = MemoryAuditService(
        repository,  # type: ignore[arg-type]
    )

    await audit.record(
        action=MemoryAuditAction.REJECTED,
        key="user_name",
        value="อะไร",
        source="rule_extractor",
        reason="question_placeholder",
    )

    events = await audit.list_recent(
        limit=10
    )

    assert len(events) == 1
    assert events[0].reason == "question_placeholder"
