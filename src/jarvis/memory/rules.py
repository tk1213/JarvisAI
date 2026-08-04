from __future__ import annotations

import re
from dataclasses import dataclass
from re import Pattern

from jarvis.memory.types import MemoryCategory, MemoryImportance


@dataclass(slots=True, frozen=True)
class MemoryRule:
    pattern: Pattern[str]
    category: MemoryCategory
    key: str
    importance: MemoryImportance


def _compile(pattern: str) -> Pattern[str]:
    return re.compile(pattern, flags=re.IGNORECASE)


MEMORY_RULES: tuple[MemoryRule, ...] = (
    MemoryRule(
        pattern=_compile(
            r"(?:ผมชื่อ|ฉันชื่อ|ดิฉันชื่อ|ชื่อของฉันคือ|my name is)"
            r"\s*(?P<value>[^,.;!?，。]+?)(?=\s+และ|$|[,.;!?，。])"
        ),
        category=MemoryCategory.PERSONAL,
        key="user_name",
        importance=MemoryImportance.HIGH,
    ),
    MemoryRule(
        pattern=_compile(
            r"(?:ลูกสาว(?:ของฉัน|ของผม)?ชื่อ|my daughter(?:'s name is| is named))"
            r"\s*(?P<value>[^,.;!?，。]+?)(?=\s+และ|$|[,.;!?，。])"
        ),
        category=MemoryCategory.FAMILY,
        key="daughter_name",
        importance=MemoryImportance.HIGH,
    ),
    MemoryRule(
        pattern=_compile(
            r"(?:ลูกชาย(?:ของฉัน|ของผม)?ชื่อ|my son(?:'s name is| is named))"
            r"\s*(?P<value>[^,.;!?，。]+?)(?=\s+และ|$|[,.;!?，。])"
        ),
        category=MemoryCategory.FAMILY,
        key="son_name",
        importance=MemoryImportance.HIGH,
    ),
    MemoryRule(
        pattern=_compile(
            r"(?:ผมชอบดื่ม|ฉันชอบดื่ม|เครื่องดื่มที่ฉันชอบคือ|"
            r"my favorite drink is|i like drinking)"
            r"\s*(?P<value>[^,.;!?，。]+?)(?=\s+และ|$|[,.;!?，。])"
        ),
        category=MemoryCategory.PREFERENCE,
        key="favorite_drink",
        importance=MemoryImportance.NORMAL,
    ),
)
