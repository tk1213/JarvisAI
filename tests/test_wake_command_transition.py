from __future__ import annotations

from unittest.mock import AsyncMock, Mock

import pytest

from jarvis.wake.activation import (
    WakeActivationResult,
    WakeActivationStatus,
)
from jarvis.wake.command_transition import WakeCommandTransition


@pytest.mark.asyncio
async def test_transition_orders_wake_ack_then_command() -> None:
    events: list[str] = []

    wake = Mock()
    wake.wait = AsyncMock(
        side_effect=lambda: (
            events.append("wake")
            or WakeActivationResult(
                status=WakeActivationStatus.DETECTED,
                score=0.91,
            )
        )
    )

    tts = Mock()
    tts.speak = AsyncMock(
        side_effect=lambda **kwargs: (
            events.append("ack")
        )
    )

    voice = Mock()
    voice.listen_for_text = AsyncMock(
        side_effect=lambda **kwargs: (
            events.append("listen")
            or "เปิดไฟ"
        )
    )

    result = await WakeCommandTransition(
        wake=wake,
        voice=voice,
        tts=tts,
    ).run(
        language="th"
    )

    assert result.completed is True
    assert result.wake_score == pytest.approx(
        0.91
    )
    assert result.transcript == "เปิดไฟ"

    assert events == [
        "wake",
        "ack",
        "listen",
    ]


@pytest.mark.asyncio
async def test_transition_returns_empty_transcript_when_no_command() -> None:
    wake = Mock()
    wake.wait = AsyncMock(
        return_value=WakeActivationResult(
            status=WakeActivationStatus.DETECTED,
            score=0.8,
        )
    )

    tts = Mock()
    tts.speak = AsyncMock()

    voice = Mock()
    voice.listen_for_text = AsyncMock(
        return_value=""
    )

    result = await WakeCommandTransition(
        wake=wake,
        voice=voice,
        tts=tts,
    ).run()

    assert result.completed is False
    assert result.transcript == ""


@pytest.mark.asyncio
async def test_transition_rejects_non_detected_activation() -> None:
    wake = Mock()
    wake.wait = AsyncMock(
        return_value=WakeActivationResult(
            status=WakeActivationStatus.CLOSED,
        )
    )

    tts = Mock()
    tts.speak = AsyncMock()

    voice = Mock()
    voice.listen_for_text = AsyncMock()

    transition = WakeCommandTransition(
        wake=wake,
        voice=voice,
        tts=tts,
    )

    with pytest.raises(
        RuntimeError,
        match="did not complete",
    ):
        await transition.run()

    tts.speak.assert_not_awaited()
    voice.listen_for_text.assert_not_awaited()
