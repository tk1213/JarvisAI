from __future__ import annotations

from enum import StrEnum


class MemoryConflictPolicy(StrEnum):
    REPLACE = "replace"
    KEEP_EXISTING = "keep_existing"
