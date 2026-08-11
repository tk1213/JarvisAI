from __future__ import annotations

from datetime import UTC, datetime

import pytest

from jarvis.conversation.turn import (
    ConversationTurnLifecycle,
    ConversationTurnSource,
    ConversationTurnStatus,
)


class Clock:
    def __init__(
        self,
        values: list[float],
    ) -> None:
        self._values = iter(
            values
        )

    def __call__(
        self,
    ) -> float:
        return next(
            self._values
        )


class TimeSource:
    def __init__(
        self,
        values: list[datetime],
    ) -> None:
        self._values = iter(
            values
        )

    def __call__(
        self,
    ) -> datetime:
        return next(
            self._values
        )


@pytest.mark.asyncio
async def test_completed_turn_has_trace_metadata() -> None:
    started = datetime(
        2026,
        8,
        5,
        10,
        0,
        tzinfo=UTC,
    )
    completed = datetime(
        2026,
        8,
        5,
        10,
        0,
        1,
        tzinfo=UTC,
    )

    lifecycle = ConversationTurnLifecycle(
        clock=Clock(
            [
                10.0,
                10.25,
            ]
        ),
        now=TimeSource(
            [
                started,
                completed,
            ]
        ),
    )

    async def handler() -> str:
        return "done"

    result = await lifecycle.run(
        user_text="hello",
        source=ConversationTurnSource.FALLBACK_AI,
        handler=handler,
    )

    assert result.turn_id
    assert len(result.turn_id) == 32
    assert result.started_at == started
    assert result.completed_at == completed
    assert result.duration_ms == pytest.approx(
        250.0
    )


@pytest.mark.asyncio
async def test_history_is_bounded() -> None:
    lifecycle = ConversationTurnLifecycle(
        max_history=2
    )

    async def handler() -> str:
        return "ok"

    for index in range(3):
        await lifecycle.run(
            user_text=f"turn-{index}",
            source=ConversationTurnSource.FALLBACK_AI,
            handler=handler,
        )

    history = lifecycle.list_recent(
        limit=10
    )

    assert len(history) == 2
    assert history[0].user_text == "turn-2"
    assert history[1].user_text == "turn-1"


@pytest.mark.asyncio
async def test_failure_is_written_to_history() -> None:
    lifecycle = ConversationTurnLifecycle()

    async def handler() -> str:
        raise RuntimeError(
            "boom"
        )

    with pytest.raises(
        RuntimeError,
        match="boom",
    ):
        await lifecycle.run(
            user_text="fail",
            source=ConversationTurnSource.PLANNER,
            handler=handler,
        )

    history = lifecycle.list_recent(
        limit=1
    )

    assert len(history) == 1
    assert history[0].status is ConversationTurnStatus.FAILED
    assert history[0].error_type == "RuntimeError"


def test_empty_turn_is_traced_and_recorded() -> None:
    lifecycle = ConversationTurnLifecycle()

    result = lifecycle.empty(
        ""
    )

    assert result.turn_id
    assert result.started_at is not None
    assert result.completed_at is not None
    assert lifecycle.list_recent(
        limit=1
    ) == (
        result,
    )


def test_clear_history_resets_last_result() -> None:
    lifecycle = ConversationTurnLifecycle()

    lifecycle.empty(
        ""
    )
    lifecycle.clear_history()

    assert lifecycle.last_result is None
    assert lifecycle.list_recent(
        limit=1
    ) == ()


def test_invalid_history_limit_is_rejected() -> None:
    lifecycle = ConversationTurnLifecycle()

    with pytest.raises(
        ValueError,
        match="limit",
    ):
        lifecycle.list_recent(
            limit=0
        )


def test_invalid_max_history_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="max_history",
    ):
        ConversationTurnLifecycle(
            max_history=0
        )


def test_naive_timestamp_is_rejected() -> None:
    lifecycle = ConversationTurnLifecycle(
        now=lambda: datetime(  # noqa: DTZ001
            2026,
            8,
            5,
            10,
            0,
        )
    )

    with pytest.raises(
        ValueError,
        match="timezone-aware",
    ):
        lifecycle.empty(
            ""
        )
