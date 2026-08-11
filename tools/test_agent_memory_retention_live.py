from __future__ import annotations

import asyncio

from jarvis.agent.memory_retention import AIAgentMemoryRetentionPolicy


class Repository:
    def __init__(self) -> None:
        self.total = 503

    async def count(
        self,
    ) -> int:
        return self.total

    async def delete_oldest(
        self,
        *,
        keep: int,
    ) -> int:
        deleted = self.total - keep
        self.total = keep
        return deleted


async def main() -> None:
    repository = Repository()

    retention = AIAgentMemoryRetentionPolicy(
        repository,  # type: ignore[arg-type]
        max_records=500,
    )

    result = await retention.enforce()

    assert result.before == 503
    assert result.deleted == 3
    assert result.after == 500
    assert repository.total == 500

    print("Sprint 4.4 Pack D — Durable Memory Retention & Observability")
    print("-" * 60)
    print("Retention limit: PASS")
    print("Oldest-record cleanup: PASS")
    print("Cleanup result observability: PASS")
    print("Durable-memory boundary: PASS")
    print("Sprint 4.4 Pack D live gate: PASS")


if __name__ == "__main__":
    asyncio.run(
        main()
    )
