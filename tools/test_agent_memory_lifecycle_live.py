from __future__ import annotations

from datetime import UTC, datetime

from jarvis.agent.memory import AIAgentMemoryLifecycle
from jarvis.planner.ai_plan_memory import AIPlanMemoryRecord, AIPlanMemoryStore


def main() -> None:
    store = AIPlanMemoryStore()

    store._records.append(  # type: ignore[attr-defined]
        AIPlanMemoryRecord(
            goal="Check Jarvis",
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
                "source": "ai_agent_runtime",
            },
        )
    )

    lifecycle = AIAgentMemoryLifecycle(
        store
    )

    snapshot = lifecycle.snapshot()

    assert snapshot.records == 1
    assert snapshot.latest_goal == "Check Jarvis"
    assert snapshot.latest_success is True
    assert snapshot.latest_source == "ai_agent_runtime"

    lifecycle.clear()

    assert lifecycle.snapshot().records == 0

    print("Sprint 4.3 Pack A — Agent Memory Lifecycle")
    print("-" * 60)
    print("Memory lifecycle abstraction: PASS")
    print("Snapshot lifecycle: PASS")
    print("Source metadata: PASS")
    print("Clear lifecycle: PASS")
    print("Sprint 4.3 Pack A live gate: PASS")


if __name__ == "__main__":
    main()
