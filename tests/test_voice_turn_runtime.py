from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, Mock

import pytest

from jarvis.voice.turn_runtime import (
    VoiceTurnRuntime,
    VoiceTurnStatus,
)


def runtime(
    *,
    transcript: str,
    reply: str,
):
    stt = Mock()
    stt.listen_vad = AsyncMock(
        return_value=transcript
    )

    conversation = Mock()
    conversation.ask = AsyncMock(
        return_value=reply
    )

    tts = Mock()
    tts.speak = AsyncMock()

    return (
        VoiceTurnRuntime(
            stt=stt,
            conversation=conversation,
            tts=tts,
        ),
        stt,
        conversation,
        tts,
    )


@pytest.mark.asyncio
async def test_complete_voice_turn() -> None:
    service, stt, conversation, tts = runtime(
        transcript="เปิดไฟ",
        reply="เปิดไฟให้แล้วครับ",
    )

    result = await service.run(
        language="th"
    )

    assert result.status is VoiceTurnStatus.COMPLETED
    assert result.transcript == "เปิดไฟ"
    assert result.reply == "เปิดไฟให้แล้วครับ"

    stt.listen_vad.assert_awaited_once_with(
        language="th"
    )
    conversation.ask.assert_awaited_once_with(
        "เปิดไฟ"
    )
    tts.speak.assert_awaited_once_with(
        "เปิดไฟให้แล้วครับ"
    )


@pytest.mark.asyncio
async def test_no_speech_stops_before_conversation() -> None:
    service, _, conversation, tts = runtime(
        transcript="",
        reply="unused",
    )

    result = await service.run()

    assert result.status is VoiceTurnStatus.NO_SPEECH
    conversation.ask.assert_not_awaited()
    tts.speak.assert_not_awaited()


@pytest.mark.asyncio
async def test_no_reply_stops_before_tts() -> None:
    service, _, conversation, tts = runtime(
        transcript="สวัสดี",
        reply="",
    )

    result = await service.run()

    assert result.status is VoiceTurnStatus.NO_REPLY
    conversation.ask.assert_awaited_once()
    tts.speak.assert_not_awaited()


@pytest.mark.asyncio
async def test_whitespace_is_normalized() -> None:
    service, _, conversation, tts = runtime(
        transcript="  ทดสอบระบบ  ",
        reply="  พร้อมใช้งาน  ",
    )

    result = await service.run()

    assert result.transcript == "ทดสอบระบบ"
    assert result.reply == "พร้อมใช้งาน"

    conversation.ask.assert_awaited_once_with(
        "ทดสอบระบบ"
    )
    tts.speak.assert_awaited_once_with(
        "พร้อมใช้งาน"
    )

@pytest.mark.asyncio
async def test_voice_turn_propagates_cancellation_from_stt() -> None:
    stt = Mock()
    stt.listen_vad = AsyncMock(
        side_effect=asyncio.CancelledError()
    )

    conversation = Mock()
    conversation.ask = AsyncMock()

    tts = Mock()
    tts.speak = AsyncMock()

    service = VoiceTurnRuntime(
        stt=stt,
        conversation=conversation,
        tts=tts,
    )

    with pytest.raises(
        asyncio.CancelledError
    ):
        await service.run()

    conversation.ask.assert_not_awaited()
    tts.speak.assert_not_awaited()

@pytest.mark.asyncio
async def test_voice_turn_propagates_cancellation_from_conversation() -> None:
    stt = Mock()
    stt.listen_vad = AsyncMock(
        return_value="hello"
    )

    conversation = Mock()
    conversation.ask = AsyncMock(
        side_effect=asyncio.CancelledError()
    )

    tts = Mock()
    tts.speak = AsyncMock()

    service = VoiceTurnRuntime(
        stt=stt,
        conversation=conversation,
        tts=tts,
    )

    with pytest.raises(
        asyncio.CancelledError
    ):
        await service.run()

    tts.speak.assert_not_awaited()