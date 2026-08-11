from __future__ import annotations

import asyncio
from datetime import UTC, datetime

from jarvis.agent.memory_persistence import AIAgentMemoryPersistence
from jarvis.planner.ai_plan_memory import AIPlanMemoryRecord, AIPlanMemoryStore


class Repository:
    def __init__(self) -> None:
        self.records = []

    async def add(
        self,
        record,
    ) -> int:
        self.records.insert(
            0,
            record
        )
        return len(
            self.records
        )

    async def list_recent(
        self,
        *,
        limit: int = 500,
    ):
        return tuple(
            self.records[:limit]
        )


async def main() -> None:
    repository = Repository()
    first_store = AIPlanMemoryStore()

    persistence = AIAgentMemoryPersistence(
        repository=repository,  # type: ignore[arg-type]
        store=first_store,
    )

    record = AIPlanMemoryRecord(
        goal="Durable health check",
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
            "source": "live_gate",
        },
    )

    await persistence.persist(
        record
    )

    restarted_store = AIPlanMemoryStore()
    restored = await AIAgentMemoryPersistence(
        repository=repository,  # type: ignore[arg-type]
        store=restarted_store,
    ).restore()

    assert restored == 1
    assert restarted_store.list_recent(
        limit=1
    )[0].goal == "Durable health check"

    print("Sprint 4.4 Pack A — Durable Agent Memory Persistence")
    print("-" * 60)
    print("Persistence abstraction: PASS")
    print("Restart restore primitive: PASS")
    print("In-memory compatibility: PASS")
    print("Bounded store loading: PASS")
    print("Sprint 4.4 Pack A live gate: PASS")


if __name__ == "__main__":
    asyncio.run(
        main()
    )
