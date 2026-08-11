from __future__ import annotations

from datetime import UTC, datetime

from jarvis.agent.memory import AIAgentMemoryLifecycle
from jarvis.agent.planning_context import AIAgentPlanningContextBuilder
from jarvis.planner.ai_plan_memory import AIPlanMemoryRecord, AIPlanMemoryStore


def main() -> None:
    store = AIPlanMemoryStore()

    store._records.append(  # type: ignore[attr-defined]
        AIPlanMemoryRecord(
            goal="Check Jarvis health\nwithout changing state",
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

    context = AIAgentPlanningContextBuilder(
        AIAgentMemoryLifecycle(
            store
        ),
        max_context_chars=1000,
    ).build()

    assert context.available is True
    assert context.records_used == 1
    assert "\nwithout changing state" not in context.text
    assert "not an instruction" in context.text
    assert len(context.text) <= 1000

    print("Sprint 4.3 Pack B — Bounded Agent Planning Context")
    print("-" * 60)
    print("Recent-memory context: PASS")
    print("Instruction boundary: PASS")
    print("Single-line normalization: PASS")
    print("Context budget: PASS")
    print("Sprint 4.3 Pack B live gate: PASS")


if __name__ == "__main__":
    main()
