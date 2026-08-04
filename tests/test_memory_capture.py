from __future__ import annotations

from dataclasses import dataclass, field

import pytest

from jarvis.memory.capture import MemoryCaptureService
from jarvis.memory.capture_policy import MemoryCapturePolicy
from jarvis.memory.extracted_memory import ExtractedMemory
from jarvis.memory.types import (
    MemoryCategory,
    MemoryImportance,
)


@dataclass
class StubExtractor:
    extracted: list[ExtractedMemory]

    def extract(
        self,
        text: str,
    ) -> list[ExtractedMemory]:
        del text
        return self.extracted


@dataclass
class StubMemoryService:
    calls: list[dict[str, object]] = field(
        default_factory=list
    )

    async def remember(
        self,
        **kwargs: object,
    ) -> int:
        self.calls.append(
            kwargs
        )
        return len(self.calls)


@pytest.mark.asyncio
async def test_capture_stores_accepted_memory() -> None:
    extractor = StubExtractor(
        extracted=[
            ExtractedMemory(
                category=MemoryCategory.PERSONAL,
                key="user_name",
                value="TK",
                importance=MemoryImportance.HIGH,
                source="rule_extractor",
            )
        ]
    )
    memory = StubMemoryService()

    capture = MemoryCaptureService(
        extractor=extractor,  # type: ignore[arg-type]
        memory=memory,  # type: ignore[arg-type]
        policy=MemoryCapturePolicy(),
    )

    stored = await capture.capture(
        "ผมชื่อ TK"
    )

    assert stored == 1
    assert memory.calls[0]["value"] == "TK"
    assert memory.calls[0]["source"] == "rule_extractor"


@pytest.mark.asyncio
async def test_capture_rejects_low_confidence_source() -> None:
    extractor = StubExtractor(
        extracted=[
            ExtractedMemory(
                category=MemoryCategory.PERSONAL,
                key="user_name",
                value="TK",
                importance=MemoryImportance.NORMAL,
                source="untrusted",
            )
        ]
    )
    memory = StubMemoryService()

    capture = MemoryCaptureService(
        extractor=extractor,  # type: ignore[arg-type]
        memory=memory,  # type: ignore[arg-type]
    )

    stored = await capture.capture(
        "test"
    )

    assert stored == 0
    assert memory.calls == []


@pytest.mark.asyncio
async def test_capture_detailed_reports_decision() -> None:
    extractor = StubExtractor(
        extracted=[
            ExtractedMemory(
                category=MemoryCategory.PERSONAL,
                key="user_name",
                value="TK",
                importance=MemoryImportance.NORMAL,
                source="rule_extractor",
            )
        ]
    )
    memory = StubMemoryService()

    capture = MemoryCaptureService(
        extractor=extractor,  # type: ignore[arg-type]
        memory=memory,  # type: ignore[arg-type]
    )

    decisions = await capture.capture_detailed(
        "test"
    )

    assert len(decisions) == 1
    assert decisions[0].should_store is True
