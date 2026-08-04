from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class MemoryAuditAction(StrEnum):
    CREATED = "created"
    UPDATED = "updated"
    UNCHANGED = "unchanged"
    DELETED = "deleted"
    REJECTED = "rejected"


@dataclass(slots=True, frozen=True)
class MemoryAuditEvent:
    action: MemoryAuditAction
    key: str
    value: str | None
    source: str
    reason: str
    created_at: datetime
