from __future__ import annotations

from enum import Enum


class MemoryCategory(str, Enum):
    PERSONAL = "personal"
    FAMILY = "family"
    SMART_HOME = "smart_home"
    PREFERENCE = "preference"
    FACT = "fact"
    SYSTEM = "system"


class MemoryImportance(int, Enum):
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3