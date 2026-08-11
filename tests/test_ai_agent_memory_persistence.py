from __future__ import annotations

from datetime import UTC, datetime

import pytest

from jarvis.agent.memory_persistence import AIAgentMemoryPersistence
from jarvis.planner.ai_plan_memory import AIPlanMemoryRecord, AIPlanMemoryStore


def make_record(
    goal: str,
) -> AIPlanMemoryRecord:
    return AIPlanMemoryRecord(
        goal=goal,
        capabilities=(
            "system.ping",
        ),
        success=True,
        completed_steps=1,
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
        metadata={
            "source": "test",
        },
    )


class FakeRepository:
    def __init__(
        self,
        records=(),
    ) -> None:
        self.records = list(
            records
        )
        self.added = []

    async def add(
        self,
        record,
    ) -> int:
        self.added.append(
            record
        )
        return len(
            self.added
        )

    async def list_recent(
        self,
        *,
        limit: int = 500,
    ):
        return tuple(
            self.records[:limit]
        )


@pytest.mark.asyncio
async def test_persist_delegates_to_repository() -> None:
    repository = FakeRepository()
    store = AIPlanMemoryStore()

    persistence = AIAgentMemoryPersistence(
        repository=repository,  # type: ignore[arg-type]
        store=store,
    )

    record = make_record(
        "Check Jarvis"
    )

    record_id = await persistence.persist(
        record
    )

    assert record_id == 1
    assert repository.added == [
        record
    ]


@pytest.mark.asyncio
async def test_restore_loads_chronological_records() -> None:
    newest = make_record(
        "Newest"
    )
    older = make_record(
        "Older"
    )

    repository = FakeRepository(
        [
            newest,
            older,
        ]
    )
    store = AIPlanMemoryStore()

    restored = await AIAgentMemoryPersistence(
        repository=repository,  # type: ignore[arg-type]
        store=store,
    ).restore()

    assert restored == 2
    assert [
        record.goal
        for record in store.list_recent(
            limit=2
        )
    ] == [
        "Newest",
        "Older",
    ]


def test_invalid_restore_limit_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="restore_limit",
    ):
        AIAgentMemoryPersistence(
            repository=FakeRepository(),  # type: ignore[arg-type]
            store=AIPlanMemoryStore(),
            restore_limit=0,
        )
