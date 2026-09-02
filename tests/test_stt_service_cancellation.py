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

@pytest.mark.asyncio
async def test_recorder_worker_preserves_caller_cancellation_when_worker_is_cancelled() -> None:
    cancel_event = threading.Event()
    worker_started = threading.Event()

    def operation() -> None:
        worker_started.set()
        cancel_event.wait()

        raise asyncio.CancelledError()

    task = asyncio.create_task(
        STTService._run_recorder_worker(
            operation,
            cancel_event=cancel_event,
            worker_name="test-recorder-worker",
        )
    )

    started = await asyncio.to_thread(
        worker_started.wait,
        1.0,
    )

    assert started is True

    task.cancel()

    with pytest.raises(
        asyncio.CancelledError
    ):
        await task

    assert cancel_event.is_set()

@pytest.mark.asyncio
async def test_recorder_worker_preserves_caller_cancellation_when_cleanup_worker_fails() -> None:
    cancel_event = threading.Event()
    worker_started = threading.Event()

    def operation() -> None:
        worker_started.set()
        cancel_event.wait()

        raise RuntimeError(
            "recorder cleanup failed"
        )

    task = asyncio.create_task(
        STTService._run_recorder_worker(
            operation,
            cancel_event=cancel_event,
            worker_name="test-recorder-worker",
        )
    )

    started = await asyncio.to_thread(
        worker_started.wait,
        1.0,
    )

    assert started is True

    task.cancel()

    with pytest.raises(
        asyncio.CancelledError
    ):
        await task

    assert cancel_event.is_set()