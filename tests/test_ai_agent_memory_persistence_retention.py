from __future__ import annotations

import asyncio
from datetime import UTC, datetime

import pytest

from jarvis.agent.memory_persistence import AIAgentMemoryPersistence
from jarvis.planner.ai_plan_memory import (
    AIPlanMemoryRecord,
    AIPlanMemoryStore,
)


class Repository:
    def __init__(self) -> None:
        self.add_calls = 0

    async def add(
        self,
        record,
    ) -> int:
        del record

        self.add_calls += 1
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


def make_record(
    goal: str,
) -> AIPlanMemoryRecord:
    return AIPlanMemoryRecord(
        goal=goal,
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


@pytest.mark.asyncio
async def test_persist_enforces_retention_after_write() -> None:
    repository = Repository()
    retention = Retention()

    persistence = AIAgentMemoryPersistence(
        repository=repository,  # type: ignore[arg-type]
        store=AIPlanMemoryStore(),
        retention=retention,  # type: ignore[arg-type]
    )

    record_id = await persistence.persist(
        make_record(
            "Check Jarvis"
        )
    )

    assert record_id == 7
    assert repository.add_calls == 1
    assert retention.calls == 1
    assert persistence.last_retention_result is not None
    assert persistence.last_retention_error is None


@pytest.mark.asyncio
async def test_retention_failure_does_not_fail_completed_persistence() -> None:
    class FailingRetention:
        async def enforce(
            self,
        ):
            raise RuntimeError(
                "retention failed"
            )

    repository = Repository()

    persistence = AIAgentMemoryPersistence(
        repository=repository,  # type: ignore[arg-type]
        store=AIPlanMemoryStore(),
        retention=FailingRetention(),  # type: ignore[arg-type]
    )

    record_id = await persistence.persist(
        make_record(
            "Check retention failure"
        )
    )

    assert record_id == 7
    assert repository.add_calls == 1
    assert persistence.last_retention_result is None
    assert persistence.last_retention_error == "retention failed"

@pytest.mark.asyncio
async def test_retention_cancellation_propagates_after_record_is_persisted() -> None:
    class CancellingRetention:
        async def enforce(
            self,
        ):
            raise asyncio.CancelledError

    repository = Repository()

    persistence = AIAgentMemoryPersistence(
        repository=repository,  # type: ignore[arg-type]
        store=AIPlanMemoryStore(),
        retention=CancellingRetention(),  # type: ignore[arg-type]
    )

    with pytest.raises(
        asyncio.CancelledError,
    ):
        await persistence.persist(
            make_record(
                "Check retention cancellation"
            )
        )

    assert repository.add_calls == 1
    assert persistence.last_retention_result is None
    assert persistence.last_retention_error is None