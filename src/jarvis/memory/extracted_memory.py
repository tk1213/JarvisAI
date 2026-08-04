from __future__ import annotations

from dataclasses import dataclass

from jarvis.memory.types import MemoryCategory, MemoryImportance


@dataclass(slots=True, frozen=True)
class ExtractedMemory:
    category: MemoryCategory
    key: str
    value: str
    importance: MemoryImportance
    source: str = "rule_extractor"

    def __post_init__(self) -> None:
        if not self.key.strip():
            raise ValueError("Extracted memory key cannot be empty.")
        if not self.value.strip():
            raise ValueError("Extracted memory value cannot be empty.")
        if not self.source.strip():
            raise ValueError("Extracted memory source cannot be empty.")
