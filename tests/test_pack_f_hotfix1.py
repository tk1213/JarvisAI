from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, Mock

import pytest

from jarvis.wake.command_transition import (
    WakeCommandTransition,
    WakeCommandTransitionResult,
    WakeCommandTransitionStage,
)
from jarvis.wake.continuous_runtime import (
    ContinuousAssistantRuntime,
    ContinuousAssistantStopReason,
)
from jarvis.wake.full_turn import (
    WakeActivatedTurnResult,
    WakeActivatedTurnRuntime,
    WakeActivatedTurnStage,
)


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
async def test_command_transition_uses_short_default_settle() -> None:
    wake = Mock()
    wake.wait = AsyncMock()
    voice = Mock()
    tts = Mock()

    transition = WakeCommandTransition(
        wake=wake,
        voice=voice,
        tts=tts,
    )

    assert transition.stage == WakeCommandTransitionStage.IDLE


@pytest.mark.asyncio
async def test_continuous_runtime_reports_cancellation_stage() -> None:
    transition = Mock()
    transition.stage = WakeCommandTransitionStage.COMMAND_LISTEN
    transition.run = AsyncMock(
        side_effect=asyncio.CancelledError
    )

    conversation = Mock()
    tts = Mock()

    turn_runtime = WakeActivatedTurnRuntime(
        transition=transition,
        conversation=conversation,
        tts=tts,
    )

    runtime = ContinuousAssistantRuntime(
        turn_runtime=turn_runtime,
    )

    result = await runtime.run(
        max_turns=2,
    )

    assert result.stop_reason == (
        ContinuousAssistantStopReason.CANCELLED
    )
    assert result.cancellation_stage is not None
    assert "transition" in result.cancellation_stage
    assert "command_listen" in result.cancellation_stage


@pytest.mark.asyncio
async def test_full_turn_stage_completes_after_empty_transcript() -> None:
    transition = Mock()
    transition.stage = WakeCommandTransitionStage.COMPLETED
    transition.run = AsyncMock(
        return_value=WakeCommandTransitionResult(
            wake_score=0.8,
            transcript="",
        )
    )

    conversation = Mock()
    tts = Mock()

    runtime = WakeActivatedTurnRuntime(
        transition=transition,
        conversation=conversation,
        tts=tts,
    )

    result = await runtime.run()

    assert result.completed is False
    assert runtime.stage == WakeActivatedTurnStage.COMPLETED
