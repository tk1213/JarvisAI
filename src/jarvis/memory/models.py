from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from jarvis.memory.types import (
    MemoryCategory,
    MemoryImportance,
)


@dataclass(slots=True)
class Memory:
    id: int | None

    category: MemoryCategory

    key: str

    value: str

    importance: MemoryImportance

    source: str

    created_at: datetime

    updated_at: datetime