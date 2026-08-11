from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import Mock

import pytest

from jarvis.agent.memory import AIAgentMemoryLifecycle
from jarvis.planner.ai_plan_memory import AIPlanMemoryRecord, AIPlanMemoryStore


def make_record(
    *,
    source: str = "test",
) -> AIPlanMemoryRecord:
    return AIPlanMemoryRecord(
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
            "source": source,
        },
    )


def test_snapshot_reports_latest_record() -> None:
    store = AIPlanMemoryStore()
    store._records.append(  # type: ignore[attr-defined]
        make_record(
            source="ai_agent_runtime"
        )
    )

    snapshot = AIAgentMemoryLifecycle(
        store
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

    assert snapshot.records == 1
    assert snapshot.latest_goal == "Check Jarvis"
    assert snapshot.latest_success is True
    assert snapshot.latest_source == "ai_agent_runtime"


def test_snapshot_handles_empty_store() -> None:
    snapshot = AIAgentMemoryLifecycle(
        AIPlanMemoryStore()
    ).snapshot()

    assert snapshot.records == 0
    assert snapshot.latest_goal is None
    assert snapshot.latest_success is None
    assert snapshot.latest_source is None


def test_snapshot_rejects_naive_timestamp() -> None:
    with pytest.raises(
        ValueError,
        match="timezone-aware",
    ):
        AIAgentMemoryLifecycle(
            AIPlanMemoryStore()
        ).snapshot(
            created_at=datetime(  # noqa: DTZ001
                2026,
                8,
                5,
                10,
                0,
            )
        )


def test_clear_delegates_to_store() -> None:
    store = AIPlanMemoryStore()
    store._records.append(  # type: ignore[attr-defined]
        make_record()
    )

    lifecycle = AIAgentMemoryLifecycle(
        store
    )

    lifecycle.clear()

    assert len(store) == 0


def test_remember_execution_rejects_empty_source() -> None:
    lifecycle = AIAgentMemoryLifecycle(
        AIPlanMemoryStore()
    )

    with pytest.raises(
        ValueError,
        match="source",
    ):
        lifecycle.remember_execution(
            execution=Mock(),
            reflection=Mock(),
            source=" ",
        )
