from __future__ import annotations

from datetime import UTC, datetime

import pytest

from jarvis.agent.memory import AIAgentMemoryLifecycle
from jarvis.agent.planning_context import AIAgentPlanningContextBuilder
from jarvis.planner.ai_plan_memory import AIPlanMemoryRecord, AIPlanMemoryStore


def make_record(
    *,
    goal: str = "Check Jarvis",
    success: bool = True,
) -> AIPlanMemoryRecord:
    return AIPlanMemoryRecord(
        goal=goal,
        capabilities=(
            "system.ping",
        ),
        success=success,
        completed_steps=1 if success else 0,
        failed_steps=0 if success else 1,
        reflection_decision="complete" if success else "review",
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


def make_builder(
    records: list[AIPlanMemoryRecord],
    **kwargs,
) -> AIAgentPlanningContextBuilder:
    store = AIPlanMemoryStore()

    store._records.extend(  # type: ignore[attr-defined]
        records
    )

    return AIAgentPlanningContextBuilder(
        AIAgentMemoryLifecycle(
            store
        ),
        **kwargs,
    )


def test_empty_memory_returns_no_context() -> None:
    context = make_builder(
        []
    ).build()

    assert context.available is False
    assert context.records_used == 0


def test_context_contains_recent_execution_summary() -> None:
    context = make_builder(
        [
            make_record(),
        ]
    ).build()

    assert context.available is True
    assert context.records_used == 1
    assert "historical planning context" in context.text
    assert "goal=Check Jarvis" in context.text
    assert "system.ping" in context.text


def test_context_normalizes_multiline_goal() -> None:
    context = make_builder(
        [
            make_record(
                goal="line one\nline two"
            ),
        ]
    ).build()

    assert "line one line two" in context.text


def test_context_respects_record_limit() -> None:
    context = make_builder(
        [
            make_record(
                goal="first"
            ),
            make_record(
                goal="second"
            ),
        ],
        max_records=1,
    ).build()

    assert context.records_used == 1
    assert "second" in context.text
    assert "first" not in context.text


def test_context_respects_character_budget() -> None:
    context = make_builder(
        [
            make_record(
                goal="x" * 1000
            ),
        ],
        max_context_chars=512,
        max_goal_chars=64,
    ).build()

    assert len(context.text) <= 512
    assert "…" in context.text


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        (
            {
                "max_records": 0,
            },
            "max_records",
        ),
        (
            {
                "max_context_chars": 255,
            },
            "max_context_chars",
        ),
        (
            {
                "max_goal_chars": 31,
            },
            "max_goal_chars",
        ),
    ],
)
def test_invalid_limits_are_rejected(
    kwargs,
    message,
) -> None:
    with pytest.raises(
        ValueError,
        match=message,
    ):
        make_builder(
            [],
            **kwargs,
        )
