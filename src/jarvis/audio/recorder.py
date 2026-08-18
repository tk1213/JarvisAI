from __future__ import annotations

import queue
import threading
import time
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import soundfile as sf

from jarvis.audio.manager import AudioManager


@dataclass(slots=True, frozen=True)
class AudioRecordingResult:
    path: Path
    sample_rate: int
    channels: int
    frames: int
    duration_seconds: float
    device_index: int

    @property
    def empty(self) -> bool:
        return self.frames == 0


@dataclass(slots=True, frozen=True)
class VADCalibration:
    noise_rms: float
    noise_mad: float
    threshold: float
    frames_used: int


@dataclass(slots=True, frozen=True)
class VADRunDiagnostics:
    threshold: float
    max_wait_rms: float
    trigger_rms: float | None
    triggered: bool


class AudioRecorder:
    def __init__(
        self,
        audio: AudioManager,
        *,
        sounddevice_module: Any | None = None,
    ) -> None:
        if sounddevice_module is None:
            import sounddevice as sounddevice_module

        self._audio = audio
        self._sounddevice = sounddevice_module
        self._last_vad_calibration: VADCalibration | None = None
        self._last_vad_run: VADRunDiagnostics | None = None

    @property
    def last_vad_calibration(
        self,
    ) -> VADCalibration | None:
        return self._last_vad_calibration

    @property
    def last_vad_run(
        self,
    ) -> VADRunDiagnostics | None:
        return self._last_vad_run

    def record(
        self,
        output: str | Path,
        *,
        seconds: float = 5.0,
        sample_rate: int | None = None,
        channels: int = 1,
    ) -> AudioRecordingResult:
        if seconds <= 0:
            raise ValueError(
                "seconds must be greater than zero."
            )

        if channels < 1:
            raise ValueError(
                "channels must be at least 1."
            )

        device = self._audio.input_info

        if channels > device.max_input_channels:
            raise ValueError(
                f"Selected input device supports only "
                f"{device.max_input_channels} input channel(s)."
            )

        rate = (
            sample_rate
            or device.default_sample_rate
        )

        if rate <= 0:
            raise ValueError(
                "sample_rate must be greater than zero."
            )

        frames = round(
            seconds * rate
        )

        if frames < 1:
            raise ValueError(
                "Recording duration produced zero frames."
            )

        data = self._sounddevice.rec(
            frames,
            samplerate=rate,
            channels=channels,
            dtype="float32",
            device=device.index,
            blocking=True,
        )

        array = np.asarray(
            data,
            dtype=np.float32,
        )

        if array.ndim == 1:
            array = array.reshape(
                -1,
                1,
            )

        output_path = Path(
            output
        )
        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        sf.write(
            output_path,
            array,
            rate,
        )

        return AudioRecordingResult(
            path=output_path,
            sample_rate=rate,
            channels=channels,
            frames=int(
                array.shape[0]
            ),
            duration_seconds=(
                float(
                    array.shape[0]
                )
                / float(
                    rate
                )
            ),
            device_index=device.index,
        )

    def calibrate_noise(
        self,
        *,
        calibration_ms: int = 500,
        vad_frame_duration_ms: int = 20,
        sample_rate: int | None = None,
        channels: int = 1,
        minimum_threshold: float = 0.005,
        mad_multiplier: float = 4.0,
        minimum_margin: float = 0.001,
        cancel_event: threading.Event | None = None,
    ) -> VADCalibration | None:
        if calibration_ms <= 0:
            raise ValueError(
                "calibration_ms must be greater than zero."
            )

        if minimum_threshold <= 0:
            raise ValueError(
                "minimum_threshold must be greater than zero."
            )

        if mad_multiplier < 0:
            raise ValueError(
                "mad_multiplier cannot be negative."
            )

        if minimum_margin < 0:
            raise ValueError(
                "minimum_margin cannot be negative."
            )

        if (
            cancel_event is not None
            and cancel_event.is_set()
        ):
            return None

        device = self._audio.input_info
        rate = (
            sample_rate
            or device.default_sample_rate
        )

        if channels < 1:
            raise ValueError(
                "channels must be at least 1."
            )

        if channels > device.max_input_channels:
            raise ValueError(
                f"Selected input device supports only "
                f"{device.max_input_channels} input channel(s)."
            )

        calibration_frames = max(
            1,
            round(
                calibration_ms
                / vad_frame_duration_ms
            ),
        )

        levels: list[float] = []

        max_stream_attempts = 3
        rearm_delay_seconds = 0.20

        last_error: RuntimeError | None = None

        for attempt in range(
            1,
            max_stream_attempts + 1,
        ):
            if (
                cancel_event is not None
                and cancel_event.is_set()
            ):
                return None

            audio_queue = self._create_audio_queue()

            try:
                with self._callback_input_stream(
                    audio_queue=audio_queue,
                    sample_rate=rate,
                    channels=channels,
                ):
                    levels = []

                    for _ in range(
                        calibration_frames
                    ):
                        if (
                            cancel_event is not None
                            and cancel_event.is_set()
                        ):
                            return None

                        try:
                            frame = self._next_callback_frame(
                                audio_queue,
                                timeout_seconds=0.1,
                            )

                        except RuntimeError:
                            if (
                                cancel_event is not None
                                and cancel_event.is_set()
                            ):
                                return None

                            raise

                        if (
                            cancel_event is not None
                            and cancel_event.is_set()
                        ):
                            return None

                        levels.append(
                            self._rms(
                                frame
                            )
                        )

                last_error = None
                break

            except RuntimeError as exc:
                if (
                    "Timed out waiting for microphone audio."
                    not in str(exc)
                ):
                    raise

                last_error = exc

                if attempt >= max_stream_attempts:
                    break

                if cancel_event is not None:
                    if cancel_event.wait(
                        rearm_delay_seconds
                    ):
                        return None
                else:
                    time.sleep(
                        rearm_delay_seconds
                    )

        if (
            cancel_event is not None
            and cancel_event.is_set()
        ):
            return None

        if last_error is not None:
            raise RuntimeError(
                "Microphone did not re-arm after "
                f"{max_stream_attempts} calibration stream attempts."
            ) from last_error

        level_array = np.asarray(
            levels,
            dtype=np.float64,
        )

        noise_rms = float(
            np.median(
                level_array
            )
        )

        noise_mad = float(
            np.median(
                np.abs(
                    level_array
                    - noise_rms
                )
            )
        )

        dynamic_margin = max(
            minimum_margin,
            noise_mad
            * mad_multiplier,
        )

        threshold = max(
            minimum_threshold,
            noise_rms
            + dynamic_margin,
        )

        calibration = VADCalibration(
            noise_rms=noise_rms,
            noise_mad=noise_mad,
            threshold=threshold,
            frames_used=calibration_frames,
        )

        self._last_vad_calibration = calibration

        return calibration

    def record_until_silence(
        self,
        *,
        output: str | Path = "record.wav",
        threshold: float = 0.005,
        vad_frame_duration_ms: int = 20,
        speech_trigger_ms: int = 100,
        silence_duration_ms: int = 900,
        pre_roll_ms: int = 300,
        max_wait_seconds: float = 10.0,
        max_record_seconds: float = 15.0,
        sample_rate: int | None = None,
        channels: int = 1,
        adaptive: bool = False,
        calibration_ms: int = 500,
        noise_multiplier: float = 1.8,
        noise_margin: float = 0.004,
        cancel_event: threading.Event | None = None,
    ) -> AudioRecordingResult | None:
        device = self._audio.input_info
        rate = (
            sample_rate
            or device.default_sample_rate
        )

        if channels < 1:
            raise ValueError(
                "channels must be at least 1."
            )

        if channels > device.max_input_channels:
            raise ValueError(
                f"Selected input device supports only "
                f"{device.max_input_channels} input channel(s)."
            )

        if threshold <= 0:
            raise ValueError(
                "threshold must be greater than zero."
            )

        if (
            cancel_event is not None
            and cancel_event.is_set()
        ):
            return None

        if adaptive:
            calibration = self.calibrate_noise(
                calibration_ms=calibration_ms,
                vad_frame_duration_ms=vad_frame_duration_ms,
                sample_rate=rate,
                channels=channels,
                minimum_threshold=threshold,
                mad_multiplier=max(
                    0.0,
                    noise_multiplier,
                ),
                minimum_margin=noise_margin,
                cancel_event=cancel_event,
            )

            if calibration is None:
                return None

            threshold = calibration.threshold

        trigger_frames = max(
            1,
            round(
                speech_trigger_ms
                / vad_frame_duration_ms
            ),
        )

        silence_frames = max(
            1,
            round(
                silence_duration_ms
                / vad_frame_duration_ms
            ),
        )

        pre_roll_frames = max(
            0,
            round(
                pre_roll_ms
                / vad_frame_duration_ms
            ),
        )

        max_wait_samples = max(
            1,
            round(
                max_wait_seconds
                * rate
            ),
        )

        max_record_samples = max(
            1,
            round(
                max_record_seconds
                * rate
            ),
        )

        pre_roll: deque[np.ndarray] = deque(
            maxlen=(
                pre_roll_frames
                or 1
            )
        )
        captured: list[np.ndarray] = []

        speech_run = 0
        silence_run = 0
        triggered = False
        max_wait_rms = 0.0
        trigger_rms: float | None = None

        waiting_samples = 0
        recording_samples = 0

        self._last_vad_run = None

        audio_queue = self._create_audio_queue()

        with self._callback_input_stream(
            audio_queue=audio_queue,
            sample_rate=rate,
            channels=channels,
        ):
            while True:
                if (
                    cancel_event is not None
                    and cancel_event.is_set()
                ):
                    return None

                try:
                    frame = self._next_callback_frame(
                        audio_queue,
                        timeout_seconds=0.1,
                    )

                except RuntimeError:
                    if (
                        cancel_event is not None
                        and cancel_event.is_set()
                    ):
                        return None

                    if not triggered:
                        self._last_vad_run = (
                            VADRunDiagnostics(
                                threshold=threshold,
                                max_wait_rms=max_wait_rms,
                                trigger_rms=None,
                                triggered=False,
                            )
                        )
                        return None

                    break

                if (
                    cancel_event is not None
                    and cancel_event.is_set()
                ):
                    return None

                rms = self._rms(
                    frame
                )

                frame_sample_count = int(
                    frame.shape[0]
                )

                if not triggered:
                    waiting_samples += frame_sample_count

                    max_wait_rms = max(
                        max_wait_rms,
                        rms,
                    )

                    pre_roll.append(
                        frame.copy()
                    )

                    if rms >= threshold:
                        speech_run += 1
                    else:
                        speech_run = 0

                    if speech_run >= trigger_frames:
                        triggered = True
                        trigger_rms = rms

                        captured.extend(
                            item.copy()
                            for item in pre_roll
                        )

                        recording_samples = sum(
                            int(
                                item.shape[0]
                            )
                            for item in pre_roll
                        )

                        silence_run = 0
                        continue

                    if (
                        waiting_samples
                        >= max_wait_samples
                    ):
                        self._last_vad_run = (
                            VADRunDiagnostics(
                                threshold=threshold,
                                max_wait_rms=max_wait_rms,
                                trigger_rms=None,
                                triggered=False,
                            )
                        )
                        return None

                    continue

                captured.append(
                    frame.copy()
                )

                recording_samples += frame_sample_count

                if rms >= threshold:
                    silence_run = 0
                else:
                    silence_run += 1

                if silence_run >= silence_frames:
                    break

                if (
                    recording_samples
                    >= max_record_samples
                ):
                    break

        self._last_vad_run = VADRunDiagnostics(
            threshold=threshold,
            max_wait_rms=max_wait_rms,
            trigger_rms=trigger_rms,
            triggered=True,
        )

        if not captured:
            return None

        array = np.concatenate(
            captured,
            axis=0,
        )

        output_path = Path(
            output
        )
        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        sf.write(
            output_path,
            array,
            rate,
        )

        return AudioRecordingResult(
            path=output_path,
            sample_rate=rate,
            channels=channels,
            frames=int(
                array.shape[0]
            ),
            duration_seconds=(
                float(
                    array.shape[0]
                )
                / float(
                    rate
                )
            ),
            device_index=device.index,
        )

    def _create_audio_queue(
        self,
    ) -> queue.Queue[np.ndarray]:
        return queue.Queue()

    def _callback_input_stream(
        self,
        *,
        audio_queue: queue.Queue[np.ndarray],
        sample_rate: int,
        channels: int,
    ) -> Any:
        device = self._audio.input_info

        def callback(
            indata: np.ndarray,
            frame_count: int,
            time_info: object,
            status: Any,
        ) -> None:
            del frame_count
            del time_info
            del status

            audio_queue.put(
                np.asarray(
                    indata,
                    dtype=np.float32,
                ).copy()
            )

        return self._sounddevice.InputStream(
            samplerate=sample_rate,
            channels=channels,
            dtype="float32",
            device=device.index,
            blocksize=0,
            latency="high",
            callback=callback,
        )

    @staticmethod
    def _next_callback_frame(
        audio_queue: queue.Queue[np.ndarray],
        *,
        timeout_seconds: float,
    ) -> np.ndarray:
        try:
            frame = audio_queue.get(
                timeout=timeout_seconds,
            )

        except queue.Empty as exc:
            raise RuntimeError(
                "Timed out waiting for microphone audio."
            ) from exc

        array = np.asarray(
            frame,
            dtype=np.float32,
        )

        if array.ndim == 1:
            array = array.reshape(
                -1,
                1,
            )

        return array

    @staticmethod
    def _rms(
        frame: np.ndarray,
    ) -> float:
        return float(
            np.sqrt(
                np.mean(
                    np.square(
                        frame,
                        dtype=np.float64,
                    )
                )
            )
        )