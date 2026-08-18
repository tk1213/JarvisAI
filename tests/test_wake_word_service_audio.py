from __future__ import annotations

import asyncio
from typing import Self
from unittest.mock import Mock, patch

import pytest

from jarvis.audio.manager import AudioManager
from jarvis.services.wake_word_service import WakeWordService


def test_wake_word_accepts_shared_audio_manager() -> None:
    audio = Mock(
        spec=AudioManager
    )

    with (
        patch(
            "jarvis.services.wake_word_service.OpenWakeWordFeatures"
        ) as features_type,
        patch(
            "jarvis.services.wake_word_service.OpenWakeWord"
        ) as wake_type,
    ):
        service = WakeWordService(
            audio=audio
        )

    assert service.audio is audio
    features_type.from_builtin.assert_called_once_with()
    wake_type.from_builtin.assert_called_once()


def test_wake_word_keeps_backward_compatible_audio_default() -> None:
    with (
        patch(
            "jarvis.services.wake_word_service.AudioManager"
        ) as audio_type,
        patch(
            "jarvis.services.wake_word_service.OpenWakeWordFeatures"
        ),
        patch(
            "jarvis.services.wake_word_service.OpenWakeWord"
        ),
    ):
        service = WakeWordService()

    assert service.audio is audio_type.return_value
    audio_type.assert_called_once_with()

@pytest.mark.asyncio
async def test_wait_for_wake_word_cancellation_closes_input_stream() -> None:
    entered = asyncio.Event()
    exited = asyncio.Event()

    class FakeInputStream:
        def __init__(
            self,
            **kwargs: object,
        ) -> None:
            del kwargs

        def __enter__(self) -> Self:
            entered.set()
            return self

        def __exit__(
            self,
            exc_type: object,
            exc_value: object,
            traceback: object,
        ) -> None:
            del exc_type
            del exc_value
            del traceback

            exited.set()

    audio = Mock(
        spec=AudioManager
    )
    audio.input_device = 1
    audio.input_info.default_sample_rate = 48000

    with (
        patch(
            "jarvis.services.wake_word_service.OpenWakeWordFeatures"
        ) as features_type,
        patch(
            "jarvis.services.wake_word_service.OpenWakeWord"
        ) as wake_type,
        patch(
            "jarvis.services.wake_word_service.sd.InputStream",
            FakeInputStream,
        ),
    ):
        features = features_type.from_builtin.return_value
        wake = wake_type.from_builtin.return_value

        features.reset = Mock()
        wake.reset = Mock()

        service = WakeWordService(
            audio=audio,
        )

        task = asyncio.create_task(
            service.wait_for_wake_word()
        )

        await entered.wait()

        task.cancel()

        with pytest.raises(
            asyncio.CancelledError,
        ):
            await task

        await asyncio.wait_for(
            exited.wait(),
            timeout=1.0,
        )

    assert exited.is_set()

@pytest.mark.asyncio
async def test_close_during_wait_stops_listener_and_closes_stream() -> None:
    entered = asyncio.Event()
    exited = asyncio.Event()

    class FakeInputStream:
        def __init__(
            self,
            **kwargs: object,
        ) -> None:
            del kwargs

        def __enter__(self) -> Self:
            entered.set()
            return self

        def __exit__(
            self,
            exc_type: object,
            exc_value: object,
            traceback: object,
        ) -> None:
            del exc_type
            del exc_value
            del traceback

            exited.set()

    audio = Mock(
        spec=AudioManager
    )
    audio.input_device = 1
    audio.input_info.default_sample_rate = 48000

    with (
        patch(
            "jarvis.services.wake_word_service.OpenWakeWordFeatures"
        ) as features_type,
        patch(
            "jarvis.services.wake_word_service.OpenWakeWord"
        ) as wake_type,
        patch(
            "jarvis.services.wake_word_service.sd.InputStream",
            FakeInputStream,
        ),
    ):
        features = features_type.from_builtin.return_value
        wake = wake_type.from_builtin.return_value

        features.reset = Mock()
        wake.reset = Mock()

        features.close = Mock()
        wake.close = Mock()

        service = WakeWordService(
            audio=audio,
        )

        task = asyncio.create_task(
            service.wait_for_wake_word()
        )

        await entered.wait()

        service.close()

        with pytest.raises(
            RuntimeError,
            match="was closed while waiting",
        ):
            await asyncio.wait_for(
                task,
                timeout=1.0,
            )

        await asyncio.wait_for(
            exited.wait(),
            timeout=1.0,
        )

    assert service.closed is True
    features.close.assert_called_once()
    wake.close.assert_called_once()
