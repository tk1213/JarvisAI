from __future__ import annotations

import asyncio
import threading
from unittest.mock import Mock

import pytest

from jarvis.services.stt_service import STTService


class BlockingRecorder:
    def __init__(self) -> None:
        self.capture_started = threading.Event()
        self.capture_stopped = threading.Event()

    def calibrate_noise(
        self,
        **kwargs: object,
    ) -> object:
        del kwargs

        calibration = Mock()
        calibration.threshold = 0.005
        return calibration

    def record_until_silence(
        self,
        **kwargs: object,
    ) -> None:
        cancel_event = kwargs.get(
            "cancel_event"
        )

        assert isinstance(
            cancel_event,
            threading.Event,
        )

        self.capture_started.set()

        cancel_event.wait()

        self.capture_stopped.set()



@pytest.mark.asyncio
async def test_listen_vad_cancellation_stops_capture_worker() -> None:
    recorder = BlockingRecorder()

    stt = Mock()

    service = STTService(
        recorder=recorder,  # type: ignore[arg-type]
        stt=stt,
    )

    listen_task = asyncio.create_task(
        service.listen_vad(
            adaptive=False,
        )
    )

    started = await asyncio.to_thread(
        recorder.capture_started.wait,
        1.0,
    )

    assert started is True

    listen_task.cancel()

    with pytest.raises(
        asyncio.CancelledError,
    ):
        await asyncio.wait_for(
            listen_task,
            timeout=1.0,
        )

    assert recorder.capture_stopped.is_set()

class BlockingCalibrationRecorder:
    def __init__(self) -> None:
        self.calibration_started = threading.Event()
        self.calibration_stopped = threading.Event()

    def calibrate_noise(
        self,
        **kwargs: object,
    ) -> None:
        cancel_event = kwargs.get(
            "cancel_event"
        )

        assert isinstance(
            cancel_event,
            threading.Event,
        )

        self.calibration_started.set()

        cancel_event.wait()

        self.calibration_stopped.set()

    def record_until_silence(
        self,
        **kwargs: object,
    ) -> None:
        raise AssertionError(
            "Capture must not start after cancelled calibration."
        )


@pytest.mark.asyncio
async def test_listen_vad_cancellation_stops_calibration_worker() -> None:
    recorder = BlockingCalibrationRecorder()

    service = STTService(
        recorder=recorder,  # type: ignore[arg-type]
        stt=Mock(),
    )

    listen_task = asyncio.create_task(
        service.listen_vad(
            adaptive=True,
        )
    )

    started = await asyncio.to_thread(
        recorder.calibration_started.wait,
        1.0,
    )

    assert started is True

    listen_task.cancel()

    with pytest.raises(
        asyncio.CancelledError,
    ):
        await asyncio.wait_for(
            listen_task,
            timeout=1.0,
        )

    assert recorder.calibration_stopped.is_set()