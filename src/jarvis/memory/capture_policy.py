from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from jarvis.memory.confidence import MemoryConfidence
from jarvis.memory.extracted_memory import ExtractedMemory
from jarvis.memory.types import MemoryImportance


@dataclass(slots=True, frozen=True)
class MemoryCaptureDecision:
    memory: ExtractedMemory
    confidence: MemoryConfidence
    should_store: bool
    reason: str


class MemoryCapturePolicy:
    _TRUSTED_SOURCES: ClassVar[
        dict[str, MemoryConfidence]
    ] = {
        "user": MemoryConfidence.VERIFIED,
        "manual": MemoryConfidence.VERIFIED,
        "manual_test": MemoryConfidence.VERIFIED,
        "manual_repair": MemoryConfidence.VERIFIED,
        "rule_extractor": MemoryConfidence.HIGH,
        "ai_extractor": MemoryConfidence.MEDIUM,
    }

    _QUESTION_VALUES: ClassVar[frozenset[str]] = frozenset(
        {
            "อะไร",
            "ใคร",
            "ที่ไหน",
            "เมื่อไหร่",
            "อย่างไร",
            "เท่าไหร่",
            "กี่",
            "what",
            "who",
            "where",
            "when",
            "how",
            "unknown",
            "none",
            "null",
        }
    )

    def __init__(
        self,
        *,
        minimum_confidence: MemoryConfidence = (
            MemoryConfidence.MEDIUM
        ),
    ) -> None:
        self._minimum_confidence = minimum_confidence

    def evaluate(
        self,
        memory: ExtractedMemory,
    ) -> MemoryCaptureDecision:
        value = memory.value.strip()
        source = memory.source.strip()

        if not value:
            return MemoryCaptureDecision(
                memory=memory,
                confidence=MemoryConfidence.LOW,
                should_store=False,
                reason="empty_value",
            )

        if value.casefold() in self._QUESTION_VALUES:
            return MemoryCaptureDecision(
                memory=memory,
                confidence=MemoryConfidence.LOW,
                should_store=False,
                reason="question_placeholder",
            )

        confidence = self._source_confidence(
            source
        )

        if memory.importance is MemoryImportance.HIGH:
            confidence = self._raise_confidence(
                confidence
            )

        should_store = (
            confidence >= self._minimum_confidence
        )

        return MemoryCaptureDecision(
            memory=memory,
            confidence=confidence,
            should_store=should_store,
            reason=(
                "accepted"
                if should_store
                else "below_confidence_threshold"
            ),
        )

    @classmethod
    def _source_confidence(
        cls,
        source: str,
    ) -> MemoryConfidence:
        normalized = source.casefold().strip()

        return cls._TRUSTED_SOURCES.get(
            normalized,
            MemoryConfidence.LOW,
        )

    @staticmethod
    def _raise_confidence(
        confidence: MemoryConfidence,
    ) -> MemoryConfidence:
        if confidence >= MemoryConfidence.HIGH:
            return confidence

        if confidence >= MemoryConfidence.MEDIUM:
            return MemoryConfidence.HIGH

        return MemoryConfidence.MEDIUM
