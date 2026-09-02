from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, Mock

import pytest

from jarvis.wake.continuous_runtime import (
    ContinuousAssistantRuntime,
    ContinuousAssistantStopReason,
)
from jarvis.wake.full_turn import WakeActivatedTurnResult


def completed(
    transcript: str,
    reply: str,
) -> WakeActivatedTurnResult:
    return WakeActivatedTurnResult(
        wake_score=0.9,
        transcript=transcript,
        reply=reply,
    )


@pytest.mark.asyncio
async def test_runtime_runs_bounded_number_of_turns() -> None:
    turn_runtime = Mock()
    turn_runtime.run = AsyncMock(
        side_effect=(
            completed(
                "สวัสดี",
                "สวัสดีครับ",
            ),
            completed(
                "วันนี้วันอะไร",
                "วันนี้คือวันเสาร์ครับ",
            ),
        )
    )

    runtime = ContinuousAssistantRuntime(
        turn_runtime=turn_runtime,
    )

    result = await runtime.run(
        language="th",
        max_turns=2,
    )

    assert result.stop_reason == (
        ContinuousAssistantStopReason.MAX_TURNS
    )
    assert len(result.turns) == 2
    assert result.completed_turns == 2
    assert runtime.running is False

    assert turn_runtime.run.await_count == 2


@pytest.mark.asyncio
async def test_runtime_preserves_silent_turn_without_execution_error() -> None:
    turn_runtime = Mock()
    turn_runtime.run = AsyncMock(
        return_value=WakeActivatedTurnResult(
            wake_score=0.8,
            transcript="",
            reply="",
        )
    )

    runtime = ContinuousAssistantRuntime(
        turn_runtime=turn_runtime,
    )

    result = await runtime.run(
        max_turns=1,
    )

    assert len(result.turns) == 1
    assert result.completed_turns == 0
    assert result.stop_reason == (
        ContinuousAssistantStopReason.MAX_TURNS
    )


@pytest.mark.asyncio
async def test_stop_request_prevents_next_turn() -> None:
    runtime: ContinuousAssistantRuntime

    async def one_turn(
        *,
        language: str,
    ) -> WakeActivatedTurnResult:
        del language

        runtime.request_stop()

        return completed(
            "ทดสอบระบบ",
            "ระบบพร้อมครับ",
        )

    turn_runtime = Mock()
    turn_runtime.run = AsyncMock(
        side_effect=one_turn,
    )

    runtime = ContinuousAssistantRuntime(
        turn_runtime=turn_runtime,
    )

    result = await runtime.run(
        max_turns=3,
    )

    assert len(result.turns) == 1
    assert result.stop_reason == (
        ContinuousAssistantStopReason.STOP_REQUESTED
    )
    assert turn_runtime.run.await_count == 1


@pytest.mark.asyncio
async def test_runtime_rejects_parallel_run() -> None:
    entered = asyncio.Event()
    release = asyncio.Event()

    async def blocked_turn(
        *,
        language: str,
    ) -> WakeActivatedTurnResult:
        del language
        entered.set()
        await release.wait()

        return completed(
            "หนึ่ง",
            "หนึ่ง",
        )

    turn_runtime = Mock()
    turn_runtime.run = AsyncMock(
        side_effect=blocked_turn,
    )

    runtime = ContinuousAssistantRuntime(
        turn_runtime=turn_runtime,
    )

    first = asyncio.create_task(
        runtime.run(
            max_turns=1,
        )
    )

    await entered.wait()

    with pytest.raises(
        RuntimeError,
        match="already running",
    ):
        await runtime.run(
            max_turns=1,
        )

    release.set()
    await first


@pytest.mark.asyncio
async def test_runtime_rejects_invalid_max_turns() -> None:
    runtime = ContinuousAssistantRuntime(
        turn_runtime=Mock(),
    )

    with pytest.raises(
        ValueError,
        match="at least 1",
    ):
        await runtime.run(
            max_turns=0,
        )

@pytest.mark.asyncio
async def test_runtime_propagates_external_caller_cancellation() -> None:
    entered = asyncio.Event()

    async def blocked_turn(
        *,
        language: str,
    ) -> WakeActivatedTurnResult:
        del language

        entered.set()
        await asyncio.Future()

        raise AssertionError(
            "unreachable"
        )

    turn_runtime = Mock()
    turn_runtime.run = AsyncMock(
        side_effect=blocked_turn,
    )

    runtime = ContinuousAssistantRuntime(
        turn_runtime=turn_runtime,
    )

    task = asyncio.create_task(
        runtime.run(
            max_turns=2,
        )
    )

    await entered.wait()

    assert runtime.running is True

    task.cancel()

    with pytest.raises(
        asyncio.CancelledError
    ):
        await task

    assert runtime.running is False

@pytest.mark.asyncio
async def test_runtime_cancellation_resets_running_before_propagating() -> None:
    entered = asyncio.Event()

    async def blocked_turn(
        *,
        language: str,
    ) -> WakeActivatedTurnResult:
        del language

        entered.set()
        await asyncio.Future()

        raise AssertionError(
            "unreachable"
        )

    turn_runtime = Mock()
    turn_runtime.run = AsyncMock(
        side_effect=blocked_turn,
    )

    runtime = ContinuousAssistantRuntime(
        turn_runtime=turn_runtime,
    )

    task = asyncio.create_task(
        runtime.run(
            max_turns=2,
        )
    )

    await entered.wait()

    assert runtime.running is True

    task.cancel()

    with pytest.raises(
        asyncio.CancelledError
    ):
        await task

    assert runtime.running is False