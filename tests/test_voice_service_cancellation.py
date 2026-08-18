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

@pytest.mark.asyncio
async def test_run_continuous_propagates_external_cancellation() -> None:
    entered = asyncio.Event()

    stt = Mock()

    async def blocked_listen(
        *,
        seconds: float,
        language: str,
    ) -> str:
        del seconds
        del language

        entered.set()
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
        service.run_continuous(
            language="th",
            idle_delay=0.0,
        )
    )

    await entered.wait()

    assert service.continuous_running is True

    task.cancel()

    with pytest.raises(
        asyncio.CancelledError,
    ):
        await task

    assert service.continuous_running is False

    assert (
        session.set_state.await_args_list[-1].args[0]
        == SessionState.IDLE
    )

@pytest.mark.asyncio
async def test_run_continuous_propagates_cancellation_during_idle_delay() -> None:
    stt = Mock()
    stt.listen = AsyncMock(
        return_value=""
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
        service.run_continuous(
            language="th",
            idle_delay=10.0,
        )
    )

    while stt.listen.await_count == 0:
        await asyncio.sleep(0)

    await asyncio.sleep(0)

    task.cancel()

    with pytest.raises(
        asyncio.CancelledError,
    ):
        await task

    assert service.continuous_running is False

    assert (
        session.set_state.await_args_list[-1].args[0]
        == SessionState.IDLE
    )