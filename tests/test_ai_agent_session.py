from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import Mock

import pytest

from jarvis.agent.memory import AIAgentMemoryLifecycle
from jarvis.agent.runtime import (
    AIAgentRunResult,
    AIAgentRunStatus,
    AIAgentRuntime,
)
from jarvis.agent.session import AIAgentSessionService
from jarvis.planner.ai_plan_memory import (
    AIPlanMemoryRecord,
    AIPlanMemoryStore,
)


def make_memory() -> AIPlanMemoryStore:
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
                "source": "ai_agent_runtime",
            },
        )
    )

    return memory


def make_runtime(
    *,
    pending: bool,
    last_result: AIAgentRunResult | None = None,
) -> Mock:
    runtime = Mock(
        spec=AIAgentRuntime
    )
    runtime.has_pending_plan = pending
    runtime.last_result = last_result
    return runtime


def test_session_snapshot_reads_pending_state_and_memory() -> None:
    memory = make_memory()
    runtime = make_runtime(
        pending=True
    )
    lifecycle = AIAgentMemoryLifecycle(
        memory
    )

    snapshot = AIAgentSessionService(
        runtime=runtime,  # type: ignore[arg-type]
        memory=memory,
        memory_lifecycle=lifecycle,
    ).snapshot(
        created_at=datetime(
            2026,
            8,
            5,
            11,
            0,
            tzinfo=UTC,
        )
    )

    assert snapshot.has_pending_plan is True
    assert snapshot.memory_records == 1
    assert snapshot.latest_goal == "Check Jarvis"
    assert snapshot.latest_success is True
    assert snapshot.latest_memory_source == "ai_agent_runtime"
    assert snapshot.last_run_status is None
    assert snapshot.last_replan_attempts == 0


def test_session_snapshot_exposes_last_replan_state() -> None:
    memory = make_memory()

    last_result = AIAgentRunResult(
        status=AIAgentRunStatus.COMPLETED,
        preview=None,
        execution=None,
        reflection=None,
        memory_record=None,
        replan_attempts=1,
    )

    snapshot = AIAgentSessionService(
        runtime=make_runtime(  # type: ignore[arg-type]
            pending=False,
            last_result=last_result,
        ),
        memory=memory,
        memory_lifecycle=AIAgentMemoryLifecycle(
            memory
        ),
    ).snapshot()

    assert snapshot.last_run_status == "completed"
    assert snapshot.last_replan_attempts == 1


def test_session_snapshot_handles_empty_memory() -> None:
    memory = AIPlanMemoryStore()

    snapshot = AIAgentSessionService(
        runtime=make_runtime(  # type: ignore[arg-type]
            pending=False
        ),
        memory=memory,
        memory_lifecycle=AIAgentMemoryLifecycle(
            memory
        ),
    ).snapshot()

    assert snapshot.memory_records == 0
    assert snapshot.latest_goal is None
    assert snapshot.latest_success is None
    assert snapshot.latest_memory_source is None


def test_session_snapshot_rejects_naive_timestamp() -> None:
    memory = AIPlanMemoryStore()

    with pytest.raises(
        ValueError,
        match="timezone-aware",
    ):
        AIAgentSessionService(
            runtime=make_runtime(  # type: ignore[arg-type]
                pending=False
            ),
            memory=memory,
            memory_lifecycle=AIAgentMemoryLifecycle(
                memory
            ),
        ).snapshot(
            created_at=datetime(  # noqa: DTZ001
                2026,
                8,
                5,
                10,
                0,
            )
        )
