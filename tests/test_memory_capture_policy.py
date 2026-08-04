from jarvis.memory.capture_policy import MemoryCapturePolicy
from jarvis.memory.confidence import MemoryConfidence
from jarvis.memory.extracted_memory import ExtractedMemory
from jarvis.memory.types import (
    MemoryCategory,
    MemoryImportance,
)


def make_memory(
    *,
    value: str = "TK",
    source: str = "rule_extractor",
    importance: MemoryImportance = MemoryImportance.NORMAL,
) -> ExtractedMemory:
    return ExtractedMemory(
        category=MemoryCategory.PERSONAL,
        key="user_name",
        value=value,
        importance=importance,
        source=source,
    )


def test_rule_extractor_is_high_confidence() -> None:
    decision = MemoryCapturePolicy().evaluate(
        make_memory()
    )

    assert decision.should_store is True
    assert decision.confidence is MemoryConfidence.HIGH
    assert decision.reason == "accepted"


def test_unknown_source_is_rejected_by_default() -> None:
    decision = MemoryCapturePolicy().evaluate(
        make_memory(
            source="unknown_source"
        )
    )

    assert decision.should_store is False
    assert decision.confidence is MemoryConfidence.LOW


def test_high_importance_raises_medium_confidence() -> None:
    decision = MemoryCapturePolicy().evaluate(
        make_memory(
            source="ai_extractor",
            importance=MemoryImportance.HIGH,
        )
    )

    assert decision.should_store is True
    assert decision.confidence is MemoryConfidence.HIGH


def test_question_placeholder_is_rejected() -> None:
    decision = MemoryCapturePolicy().evaluate(
        make_memory(
            value="อะไร"
        )
    )

    assert decision.should_store is False
    assert decision.reason == "question_placeholder"


def test_manual_source_is_verified() -> None:
    decision = MemoryCapturePolicy().evaluate(
        make_memory(
            source="manual"
        )
    )

    assert decision.should_store is True
    assert decision.confidence is MemoryConfidence.VERIFIED
