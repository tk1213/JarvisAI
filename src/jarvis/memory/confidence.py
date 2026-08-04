from __future__ import annotations

from enum import IntEnum


class MemoryConfidence(IntEnum):
    LOW = 25
    MEDIUM = 60
    HIGH = 85
    VERIFIED = 100
