from __future__ import annotations

import asyncio

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


@pytest.mark.asyncio
async def test_turn_lifecycle_records_completed_turn() -> None:
    lifecycle = ConversationTurnLifecycle(
        clock=Clock(
            [
                10.0,
                10.125,
            ]
        )
    )

    async def handler() -> str:
        return "Jarvis is ready."

    result = await lifecycle.run(
        user_text="hello",
        source=ConversationTurnSource.FALLBACK_AI,
        handler=handler,
    )

    assert result.status is ConversationTurnStatus.COMPLETED
    assert result.success is True
    assert result.failed is False
    assert result.reply == "Jarvis is ready."
    assert result.source is ConversationTurnSource.FALLBACK_AI
    assert result.duration_ms == pytest.approx(
        125.0
    )
    assert result.error_type is None
    assert lifecycle.last_result is result


@pytest.mark.asyncio
async def test_turn_lifecycle_records_failure_before_reraising() -> None:
    lifecycle = ConversationTurnLifecycle(
        clock=Clock(
            [
                20.0,
                20.05,
            ]
        )
    )

    async def handler() -> str:
        raise RuntimeError(
            "test failure"
        )

    with pytest.raises(
        RuntimeError,
        match="test failure",
    ):
        await lifecycle.run(
            user_text="fail",
            source=ConversationTurnSource.NATIVE_TOOL,
            handler=handler,
        )

    result = lifecycle.last_result

    assert result is not None
    assert result.status is ConversationTurnStatus.FAILED
    assert result.failed is True
    assert result.reply == ""
    assert result.error_type == "RuntimeError"
    assert result.duration_ms == pytest.approx(
        50.0
    )


def test_empty_turn_has_zero_duration() -> None:
    lifecycle = ConversationTurnLifecycle()

    result = lifecycle.empty(
        "   "
    )

    assert result.status is ConversationTurnStatus.EMPTY
    assert result.source is ConversationTurnSource.UNKNOWN
    assert result.duration_ms == 0.0
    assert result.reply == ""
    assert lifecycle.last_result is result


def test_turn_source_values_are_stable() -> None:
    assert ConversationTurnSource.AI_AGENT.value == "ai_agent"
    assert ConversationTurnSource.PLANNER.value == "planner"
    assert ConversationTurnSource.NATIVE_TOOL.value == "native_tool"
    assert ConversationTurnSource.CAPABILITY.value == "capability"
    assert ConversationTurnSource.FALLBACK_AI.value == "fallback_ai"

@pytest.mark.asyncio
async def test_turn_cancellation_clears_active_source() -> None:
    lifecycle = ConversationTurnLifecycle()

    started = asyncio.Event()

    async def handler() -> str:
        started.set()
        await asyncio.Future()
        return "never"

    task = asyncio.create_task(
        lifecycle.run(
            user_text="cancel me",
            source=ConversationTurnSource.PLANNER,
            handler=handler,
        )
    )

    await started.wait()

    assert (
        lifecycle.active_source
        is ConversationTurnSource.PLANNER
    )

    task.cancel()

    with pytest.raises(
        asyncio.CancelledError
    ):
        await task

    assert lifecycle.active_source is None

@pytest.mark.asyncio
async def test_turn_cancellation_does_not_overwrite_last_result() -> None:
    lifecycle = ConversationTurnLifecycle()

    async def completed_handler() -> str:
        return "done"

    previous = await lifecycle.run(
        user_text="first",
        source=ConversationTurnSource.FALLBACK_AI,
        handler=completed_handler,
    )

    started = asyncio.Event()

    async def blocked_handler() -> str:
        started.set()
        await asyncio.Future()
        return "never"

    task = asyncio.create_task(
        lifecycle.run(
            user_text="second",
            source=ConversationTurnSource.PLANNER,
            handler=blocked_handler,
        )
    )

    await started.wait()
    task.cancel()

    with pytest.raises(
        asyncio.CancelledError
    ):
        await task

    assert lifecycle.last_result is previous
    assert lifecycle.active_source is None