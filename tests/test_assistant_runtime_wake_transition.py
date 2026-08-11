from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, Mock

import pytest

from jarvis.core.session import SessionState
from jarvis.services.assistant_runtime_service import AssistantRuntimeService


@pytest.mark.asyncio
async def test_wake_cycle_acknowledges_before_listening() -> None:
    events: list[str] = []

    wake_word = Mock()
    wake_word.wait_for_wake_word = AsyncMock(
        side_effect=lambda: events.append("wake") or 0.91
    )

    voice = Mock()
    voice.listen_for_text = AsyncMock(
        side_effect=lambda **kwargs: events.append("listen") or ""
    )

    conversation = Mock()
    conversation.has_pending_smart_home = False

    tts = Mock()
    tts.speak = AsyncMock()

    session = Mock()
    session.set_state = AsyncMock()

    runtime = AssistantRuntimeService(
        wake_word=wake_word,
        voice=voice,
        conversation=conversation,
        tts=tts,
        session=session,
    )
    runtime._running = True

    async def acknowledge() -> None:
        events.append("ack")

    runtime._acknowledge_wake = acknowledge  # type: ignore[method-assign]

    await runtime._run_wake_cycle(
        language="th"
    )

    assert events == [
        "wake",
        "ack",
        "listen",
    ]


@pytest.mark.asyncio
async def test_stopped_runtime_does_not_acknowledge_after_wake() -> None:
    wake_word = Mock()

    runtime = AssistantRuntimeService(
        wake_word=wake_word,
        voice=Mock(),
        conversation=Mock(),
        tts=Mock(),
        session=Mock(),
    )

    async def detect_and_stop() -> float:
        runtime.stop()
        return 0.95

    wake_word.wait_for_wake_word = AsyncMock(
        side_effect=detect_and_stop
    )
    runtime._acknowledge_wake = AsyncMock()  # type: ignore[method-assign]

    runtime._running = True

    await runtime._run_wake_cycle(
        language="th"
    )

    runtime._acknowledge_wake.assert_not_awaited()  # type: ignore[attr-defined]

@pytest.mark.asyncio
async def test_runtime_recovers_from_cycle_error_and_runs_next_cycle() -> None:
    wake_word = Mock()
    voice = Mock()
    conversation = Mock()
    tts = Mock()
    session = Mock()

    conversation.has_pending_smart_home = False
    session.set_state = AsyncMock()

    runtime = AssistantRuntimeService(
        wake_word=wake_word,
        voice=voice,
        conversation=conversation,
        tts=tts,
        session=session,
        error_retry_delay=0.0,
    )

    cycle_count = 0

    async def controlled_cycle(
        *,
        language: str,
    ) -> None:
        nonlocal cycle_count

        assert language == "th"

        cycle_count += 1

        if cycle_count == 1:
            raise RuntimeError(
                "controlled cycle failure"
            )

        runtime.stop()

    runtime._run_wake_cycle = controlled_cycle  # type: ignore[method-assign]

    await runtime.run(
        language="th",
    )

    assert cycle_count == 2
    assert runtime.running is False

    session.set_state.assert_awaited_once()

@pytest.mark.asyncio
async def test_runtime_recovery_survives_session_reset_failure() -> None:
    wake_word = Mock()
    voice = Mock()
    conversation = Mock()
    tts = Mock()
    session = Mock()

    conversation.has_pending_smart_home = False
    session.set_state = AsyncMock(
        side_effect=RuntimeError(
            "controlled session reset failure"
        )
    )

    runtime = AssistantRuntimeService(
        wake_word=wake_word,
        voice=voice,
        conversation=conversation,
        tts=tts,
        session=session,
        error_retry_delay=0.0,
    )

    cycle_count = 0

    async def controlled_cycle(
        *,
        language: str,
    ) -> None:
        nonlocal cycle_count

        assert language == "th"

        cycle_count += 1

        if cycle_count == 1:
            raise RuntimeError(
                "controlled cycle failure"
            )

        runtime.stop()

    runtime._run_wake_cycle = controlled_cycle  # type: ignore[method-assign]

    await runtime.run(
        language="th",
    )

    assert cycle_count == 2
    assert runtime.running is False
    assert session.set_state.await_count == 1

@pytest.mark.asyncio
async def test_runtime_recovery_cancels_pending_smart_home_action() -> None:
    wake_word = Mock()
    voice = Mock()
    conversation = Mock()
    tts = Mock()
    session = Mock()

    conversation.has_pending_smart_home = True
    conversation.cancel_pending_smart_home = Mock(
        return_value=True
    )

    session.set_state = AsyncMock()

    runtime = AssistantRuntimeService(
        wake_word=wake_word,
        voice=voice,
        conversation=conversation,
        tts=tts,
        session=session,
        error_retry_delay=0.0,
    )

    cycle_count = 0

    async def controlled_cycle(
        *,
        language: str,
    ) -> None:
        nonlocal cycle_count

        assert language == "th"

        cycle_count += 1

        if cycle_count == 1:
            raise RuntimeError(
                "controlled cycle failure"
            )

        runtime.stop()

    runtime._run_wake_cycle = controlled_cycle  # type: ignore[method-assign]

    await runtime.run(
        language="th",
    )

    assert cycle_count == 2
    assert runtime.running is False

    conversation.cancel_pending_smart_home.assert_called_once()

    session.set_state.assert_awaited_once()

@pytest.mark.asyncio
async def test_runtime_tts_failure_is_contained_and_session_returns_idle() -> None:
    wake_word = Mock()
    voice = Mock()
    conversation = Mock()

    conversation.has_pending_smart_home = False

    tts = Mock()
    tts.speak = AsyncMock(
        side_effect=RuntimeError(
            "controlled TTS failure"
        )
    )

    session = Mock()
    session.set_state = AsyncMock()

    runtime = AssistantRuntimeService(
        wake_word=wake_word,
        voice=voice,
        conversation=conversation,
        tts=tts,
        session=session,
        error_retry_delay=0.0,
    )

    await runtime._speak_runtime_reply(
        "test reply",
        output="test_runtime_reply.wav",
    )

    tts.speak.assert_awaited_once_with(
        text="test reply",
        output="test_runtime_reply.wav",
    )

    assert session.set_state.await_count == 2

    assert (
        session.set_state.await_args_list[0].args[0]
        == SessionState.SPEAKING
    )

    assert (
        session.set_state.await_args_list[1].args[0]
        == SessionState.IDLE
    )

@pytest.mark.asyncio
async def test_runtime_handles_cancellation_without_recovery() -> None:
    wake_word = Mock()
    wake_word.wait_for_wake_word = AsyncMock(
        side_effect=asyncio.CancelledError()
    )

    voice = Mock()
    conversation = Mock()
    tts = Mock()
    session = Mock()

    runtime = AssistantRuntimeService(
        wake_word=wake_word,
        voice=voice,
        conversation=conversation,
        tts=tts,
        session=session,
        error_retry_delay=0.0,
    )

    runtime._recover_from_cycle_error = AsyncMock()  # type: ignore[method-assign]

    await runtime.run(
        language="th",
    )

    runtime._recover_from_cycle_error.assert_not_awaited()  # type: ignore[attr-defined]

    wake_word.wait_for_wake_word.assert_awaited_once_with()

    assert runtime.running is False