from __future__ import annotations

from unittest.mock import AsyncMock, Mock, patch

import pytest

from jarvis.wake.activation import (
    WakeActivationResult,
    WakeActivationStatus,
)
from jarvis.wake.command_transition import WakeCommandTransition


@pytest.mark.asyncio
async def test_transition_waits_after_ack_before_listening() -> None:
    events: list[str] = []

    wake = Mock()
    wake.wait = AsyncMock(
        return_value=WakeActivationResult(
            status=WakeActivationStatus.DETECTED,
            score=0.9,
        )
    )

    tts = Mock()
    tts.speak = AsyncMock(
        side_effect=lambda **kwargs: events.append(
            "ack"
        )
    )

    voice = Mock()
    voice.listen_for_text = AsyncMock(
        side_effect=lambda **kwargs: (
            events.append("listen")
            or ""
        )
    )

    async def fake_sleep(
        seconds: float,
    ) -> None:
        assert seconds == pytest.approx(
            0.8
        )
        events.append(
            "settle"
        )

    with patch(
        "jarvis.wake.command_transition.asyncio.sleep",
        side_effect=fake_sleep,
    ):
        await WakeCommandTransition(
            wake=wake,
            voice=voice,
            tts=tts,
            post_ack_settle_seconds=0.8,
        ).run()

    assert events == [
        "ack",
        "settle",
        "listen",
    ]


def test_negative_settle_delay_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="cannot be negative",
    ):
        WakeCommandTransition(
            wake=Mock(),
            voice=Mock(),
            tts=Mock(),
            post_ack_settle_seconds=-0.1,
        )
