from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, Mock

import pytest

from jarvis.wake.command_transition import WakeCommandTransitionResult
from jarvis.wake.full_turn import (
    WakeActivatedTurnRuntime,
    WakeActivatedTurnStage,
)


@pytest.mark.asyncio
async def test_full_turn_routes_transcript_to_conversation_and_tts() -> None:
    transition = Mock()
    transition.run = AsyncMock(
        return_value=WakeCommandTransitionResult(
            wake_score=0.91,
            transcript="วันนี้วันอะไร",
        )
    )

    conversation = Mock()
    conversation.ask = AsyncMock(
        return_value="วันนี้คือวันเสาร์ครับ"
    )

    tts = Mock()
    tts.speak = AsyncMock()

    result = await WakeActivatedTurnRuntime(
        transition=transition,
        conversation=conversation,
        tts=tts,
    ).run(
        language="th",
    )

    assert result.completed is True
    assert result.wake_score == pytest.approx(
        0.91
    )
    assert result.transcript == "วันนี้วันอะไร"
    assert result.reply == "วันนี้คือวันเสาร์ครับ"

    transition.run.assert_awaited_once_with(
        language="th",
    )
    conversation.ask.assert_awaited_once_with(
        "วันนี้วันอะไร",
        voice_mode=True,
    )
    tts.speak.assert_awaited_once_with(
        text="วันนี้คือวันเสาร์ครับ",
        output="wake_turn_reply.wav",
    )


@pytest.mark.asyncio
async def test_empty_transcript_never_reaches_conversation_or_tts() -> None:
    transition = Mock()
    transition.run = AsyncMock(
        return_value=WakeCommandTransitionResult(
            wake_score=0.88,
            transcript="",
        )
    )

    conversation = Mock()
    conversation.ask = AsyncMock()

    tts = Mock()
    tts.speak = AsyncMock()

    result = await WakeActivatedTurnRuntime(
        transition=transition,
        conversation=conversation,
        tts=tts,
    ).run()

    assert result.completed is False
    assert result.transcript == ""
    assert result.reply == ""

    conversation.ask.assert_not_awaited()
    tts.speak.assert_not_awaited()


@pytest.mark.asyncio
async def test_empty_reply_is_not_spoken() -> None:
    transition = Mock()
    transition.run = AsyncMock(
        return_value=WakeCommandTransitionResult(
            wake_score=0.77,
            transcript="ทดสอบระบบ",
        )
    )

    conversation = Mock()
    conversation.ask = AsyncMock(
        return_value=""
    )

    tts = Mock()
    tts.speak = AsyncMock()

    result = await WakeActivatedTurnRuntime(
        transition=transition,
        conversation=conversation,
        tts=tts,
    ).run()

    assert result.completed is False
    assert result.transcript == "ทดสอบระบบ"
    assert result.reply == ""

    conversation.ask.assert_awaited_once_with(
        "ทดสอบระบบ",
        voice_mode=True,
    )
    tts.speak.assert_not_awaited()

@pytest.mark.asyncio
async def test_full_turn_preserves_conversation_stage_on_cancellation() -> None:
    transition = Mock()
    transition.run = AsyncMock(
        return_value=WakeCommandTransitionResult(
            wake_score=0.9,
            transcript="hello",
        )
    )

    conversation = Mock()
    conversation.ask = AsyncMock(
        side_effect=asyncio.CancelledError()
    )

    tts = Mock()
    tts.speak = AsyncMock()

    runtime = WakeActivatedTurnRuntime(
        transition=transition,
        conversation=conversation,
        tts=tts,
    )

    with pytest.raises(
        asyncio.CancelledError
    ):
        await runtime.run()

    assert runtime.stage is (
        WakeActivatedTurnStage.CONVERSATION
    )
    tts.speak.assert_not_awaited()


@pytest.mark.asyncio
async def test_full_turn_preserves_tts_stage_on_cancellation() -> None:
    transition = Mock()
    transition.run = AsyncMock(
        return_value=WakeCommandTransitionResult(
            wake_score=0.9,
            transcript="hello",
        )
    )

    conversation = Mock()
    conversation.ask = AsyncMock(
        return_value="reply"
    )

    tts = Mock()
    tts.speak = AsyncMock(
        side_effect=asyncio.CancelledError()
    )

    runtime = WakeActivatedTurnRuntime(
        transition=transition,
        conversation=conversation,
        tts=tts,
    )

    with pytest.raises(
        asyncio.CancelledError
    ):
        await runtime.run()

    assert runtime.stage is (
        WakeActivatedTurnStage.TTS_REPLY
    )