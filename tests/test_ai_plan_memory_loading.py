from __future__ import annotations

from datetime import UTC, datetime

from jarvis.planner.ai_plan_memory import AIPlanMemoryRecord, AIPlanMemoryStore


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


def test_load_records_replaces_existing_records() -> None:
    store = AIPlanMemoryStore()

    store.load_records(
        (
            make_record(
                "first"
            ),
        )
    )

    store.load_records(
        (
            make_record(
                "second"
            ),
        ),
        replace=True,
    )

    assert len(store) == 1
    assert store.list_recent(
        limit=1
    )[0].goal == "second"


def test_load_records_respects_store_limit() -> None:
    store = AIPlanMemoryStore(
        max_records=2
    )

    store.load_records(
        (
            make_record(
                "one"
            ),
            make_record(
                "two"
            ),
            make_record(
                "three"
            ),
        )
    )

    assert len(store) == 2
    assert [
        item.goal
        for item in store.list_recent(
            limit=2
        )
    ] == [
        "three",
        "two",
    ]
