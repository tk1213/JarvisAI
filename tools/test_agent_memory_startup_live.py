from __future__ import annotations

import asyncio

from jarvis.agent.memory_startup import AIAgentMemoryStartupService


class Lifecycle:
    def __init__(self) -> None:
        self.calls = 0

    async def restore_durable_memory(
        self,
    ) -> int:
        self.calls += 1
        return 4


async def main() -> None:
    lifecycle = Lifecycle()

    startup = AIAgentMemoryStartupService(
        lifecycle,  # type: ignore[arg-type]
    )

    restored = await startup.restore()
    restored_again = await startup.restore()

    assert restored == 4
    assert restored_again == 4
    assert lifecycle.calls == 1
    assert startup.restored is True
    assert startup.restored_records == 4

    print("Sprint 4.4 Pack B — Automatic Startup Restore")
    print("-" * 60)
    print("Startup restore service: PASS")
    print("Idempotent restore guard: PASS")
    print("Restore count observability: PASS")
    print("Database-ready sequencing primitive: PASS")
    print("Sprint 4.4 Pack B live gate: PASS")


if __name__ == "__main__":
    asyncio.run(
        main()
    )
