from __future__ import annotations

from datetime import UTC, datetime

import pytest

from jarvis.agent.memory_persistence import AIAgentMemoryPersistence
from jarvis.planner.ai_plan_memory import AIPlanMemoryRecord, AIPlanMemoryStore


class Repository:
    async def add(
        self,
        record,
    ) -> int:
        del record
        return 7

    async def list_recent(
        self,
        *,
        limit: int = 500,
    ):
        del limit
        return ()


class Retention:
    def __init__(self) -> None:
        self.calls = 0

    async def enforce(
        self,
    ):
        self.calls += 1
        return object()


@pytest.mark.asyncio
async def test_persist_enforces_retention_after_write() -> None:
    retention = Retention()

    persistence = AIAgentMemoryPersistence(
        repository=Repository(),  # type: ignore[arg-type]
        store=AIPlanMemoryStore(),
        retention=retention,  # type: ignore[arg-type]
    )

    record = AIPlanMemoryRecord(
        goal="Check Jarvis",
        capabilities=(),
        success=True,
        completed_steps=0,
        failed_steps=0,
        reflection_decision="complete",
        created_at=datetime(
            2026,
            8,
            5,
            10,
            0,
            tzinfo=UTC,
        ),
        metadata={},
    )

    record_id = await persistence.persist(
        record
    )

    assert record_id == 7
    assert retention.calls == 1
    assert persistence.last_retention_result is not None
