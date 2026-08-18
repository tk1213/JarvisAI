from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, Mock

import pytest

from jarvis.core.session import SessionState
from jarvis.services.voice_service import VoiceService


@pytest.mark.asyncio
async def test_listen_for_text_cancellation_restores_idle_state() -> None:
    stt = Mock()

    async def blocked_listen(
        *,
        seconds: float,
        language: str,
    ) -> str:
        del seconds
        del language

        await asyncio.Future()
        return ""

    stt.listen = AsyncMock(
        side_effect=blocked_listen,
    )

    session = Mock()
    session.set_state = AsyncMock()

    service = VoiceService(
        stt=stt,
        conversation=Mock(),
        tts=Mock(),
        session=session,
    )

    task = asyncio.create_task(
        service.listen_for_text(
            language="th",
        )
    )

    await asyncio.sleep(0)

    task.cancel()

    with pytest.raises(
        asyncio.CancelledError,
    ):
        await task

    assert (
        session.set_state.await_args_list[-1].args[0]
        == SessionState.IDLE
    )