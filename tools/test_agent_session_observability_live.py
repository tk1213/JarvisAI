from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import Mock

from jarvis.agent.memory import AIAgentMemoryLifecycle
from jarvis.agent.runtime import (
    AIAgentRunResult,
    AIAgentRunStatus,
    AIAgentRuntime,
)
from jarvis.agent.session import AIAgentSessionService
from jarvis.planner.ai_plan_memory import AIPlanMemoryRecord, AIPlanMemoryStore


def main() -> None:
    memory = AIPlanMemoryStore()

    memory._records.append(  # type: ignore[attr-defined]
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
                "source": "ai_agent_runtime_replanned",
            },
        )
    )

    runtime = Mock(
        spec=AIAgentRuntime
    )
    runtime.has_pending_plan = False
    runtime.last_result = AIAgentRunResult(
        status=AIAgentRunStatus.COMPLETED,
        preview=None,
        execution=None,
        reflection=None,
        memory_record=None,
        replan_attempts=1,
    )

    snapshot = AIAgentSessionService(
        runtime=runtime,  # type: ignore[arg-type]
        memory=memory,
        memory_lifecycle=AIAgentMemoryLifecycle(
            memory
        ),
    ).snapshot()

    assert snapshot.memory_records == 1
    assert snapshot.latest_memory_source == "ai_agent_runtime_replanned"
    assert snapshot.last_run_status == "completed"
    assert snapshot.last_replan_attempts == 1

    print("Sprint 4.3 Pack D — Session & Replan Observability")
    print("-" * 60)
    print("Memory lifecycle snapshot: PASS")
    print("Latest memory source: PASS")
    print("Last run status: PASS")
    print("Replan attempt observability: PASS")
    print("Sprint 4.3 Pack D live gate: PASS")


if __name__ == "__main__":
    main()
