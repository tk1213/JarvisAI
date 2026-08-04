from __future__ import annotations

from jarvis.memory.capture_policy import MemoryCapturePolicy
from jarvis.memory.extracted_memory import ExtractedMemory
from jarvis.memory.types import (
    MemoryCategory,
    MemoryImportance,
)


def show(
    memory: ExtractedMemory,
) -> None:
    decision = MemoryCapturePolicy().evaluate(
        memory
    )

    print(
        f"{memory.key}={memory.value!r} "
        f"source={memory.source!r} "
        f"confidence={decision.confidence.name} "
        f"store={decision.should_store} "
        f"reason={decision.reason}"
    )


def main() -> None:
    show(
        ExtractedMemory(
            category=MemoryCategory.PERSONAL,
            key="user_name",
            value="TK",
            importance=MemoryImportance.HIGH,
            source="rule_extractor",
        )
    )

    show(
        ExtractedMemory(
            category=MemoryCategory.PERSONAL,
            key="user_name",
            value="อะไร",
            importance=MemoryImportance.HIGH,
            source="rule_extractor",
        )
    )

    show(
        ExtractedMemory(
            category=MemoryCategory.PERSONAL,
            key="user_name",
            value="TK",
            importance=MemoryImportance.NORMAL,
            source="unknown_source",
        )
    )


if __name__ == "__main__":
    main()
