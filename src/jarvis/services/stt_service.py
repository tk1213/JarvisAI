from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import resample_poly

from jarvis.audio.recorder import (
    AudioRecorder,
    AudioRecordingResult,
)
from jarvis.audio.signal_diagnostics import (
    AudioSignalAnalyzer,
    AudioSignalDiagnostics,
)
from jarvis.speech.stt import SpeechToText


@dataclass(slots=True, frozen=True)
class STTTimingDiagnostics:
    calibration_seconds: float = 0.0
    capture_seconds: float = 0.0
    diagnostics_seconds: float = 0.0
    normalization_seconds: float = 0.0
    transcription_seconds: float = 0.0

    @property
    def total_seconds(self) -> float:
        return (
            self.calibration_seconds
            + self.capture_seconds
            + self.diagnostics_seconds
            + self.normalization_seconds
            + self.transcription_seconds
        )


class STTService:
    def __init__(
        self,
        recorder: AudioRecorder,
        stt: SpeechToText,
        *,
        signal_analyzer: AudioSignalAnalyzer | None = None,
    ) -> None:
        self.recorder = recorder
        self.stt = stt
        self.signal_analyzer = (
            signal_analyzer
            if signal_analyzer is not None
            else AudioSignalAnalyzer()
        )
        self._last_signal: AudioSignalDiagnostics | None = None
        self._last_timing: STTTimingDiagnostics | None = None

    @property
    def last_signal(
        self,
    ) -> AudioSignalDiagnostics | None:
        return self._last_signal

    @property
    def last_timing(
        self,
    ) -> STTTimingDiagnostics | None:
        return self._last_timing

    async def listen(
        self,
        seconds: float = 5.0,
        language: str = "th",
    ) -> str:
        del seconds

        return await self.listen_vad(
            language=language,
        )

    async def listen_vad(
        self,
        language: str = "th",
        output: str = "record.wav",
        *,
        threshold: float = 0.005,
        vad_frame_duration_ms: int = 20,
        speech_trigger_ms: int = 100,
        silence_duration_ms: int = 900,
        pre_roll_ms: int = 300,
        max_wait_seconds: float = 10.0,
        max_record_seconds: float = 15.0,
        adaptive: bool = True,
        calibration_ms: int = 200,
        mad_multiplier: float = 4.0,
        minimum_margin: float = 0.001,
    ) -> str:
        active_threshold = threshold

        calibration_seconds = 0.0
        capture_seconds = 0.0

        if adaptive:
            calibration_started = time.perf_counter()

            calibration = self.recorder.calibrate_noise(
                calibration_ms=calibration_ms,
                vad_frame_duration_ms=vad_frame_duration_ms,
                minimum_threshold=threshold,
                mad_multiplier=mad_multiplier,
                minimum_margin=minimum_margin,
            )

            calibration_seconds = (
                time.perf_counter()
                - calibration_started
            )

            active_threshold = calibration.threshold

        capture_started = time.perf_counter()

        audio_file = self.recorder.record_until_silence(
            output=output,
            threshold=active_threshold,
            vad_frame_duration_ms=vad_frame_duration_ms,
            speech_trigger_ms=speech_trigger_ms,
            silence_duration_ms=silence_duration_ms,
            pre_roll_ms=pre_roll_ms,
            max_wait_seconds=max_wait_seconds,
            max_record_seconds=max_record_seconds,
            adaptive=False,
        )

        capture_seconds = (
            time.perf_counter()
            - capture_started
        )

        if audio_file is None:
            self._last_timing = STTTimingDiagnostics(
                calibration_seconds=calibration_seconds,
                capture_seconds=capture_seconds,
            )
            return ""

        audio_path = self._coerce_audio_path(
            audio_file
        )

        return await self._transcribe_validated(
            audio_path,
            language=language,
            calibration_seconds=calibration_seconds,
            capture_seconds=capture_seconds,
        )

    async def listen_fixed(
        self,
        seconds: float = 5.0,
        language: str = "th",
        output: str = "record.wav",
    ) -> str:
        recording = self.recorder.record(
            seconds=seconds,
            output=output,
        )

        audio_path = self._coerce_audio_path(
            recording
        )

        return await self._transcribe_validated(
            audio_path,
            language=language,
        )

    async def transcribe_file(
        self,
        audio_file: str | Path,
        language: str = "th",
        *,
        validate_signal: bool = True,
    ) -> str:
        audio_path = Path(
            audio_file
        )

        if validate_signal:
            return await self._transcribe_validated(
                audio_path,
                language=language,
            )

        return await self._transcribe(
            audio_path,
            language=language,
        )

    @staticmethod
    def _normalize_for_stt(
        audio_file: str | Path,
        *,
        target_rate: int = 16000,
    ) -> Path:
        source_path = Path(
            audio_file
        )

        if not source_path.exists():
            return source_path

        data, source_rate = sf.read(
            source_path,
            dtype="float32",
            always_2d=False,
        )

        if source_rate == target_rate:
            return source_path

        common_divisor = int(
            np.gcd(
                source_rate,
                target_rate,
            )
        )

        up = target_rate // common_divisor
        down = source_rate // common_divisor

        normalized = resample_poly(
            data,
            up=up,
            down=down,
            axis=0,
        )

        output_path = source_path.with_name(
            f"{source_path.stem}_stt.wav"
        )

        sf.write(
            output_path,
            np.asarray(
                normalized,
                dtype=np.float32,
            ),
            target_rate,
        )

        return output_path

    async def _transcribe_validated(
        self,
        audio_file: str | Path,
        *,
        language: str,
        calibration_seconds: float = 0.0,
        capture_seconds: float = 0.0,
    ) -> str:
        diagnostics_started = time.perf_counter()

        diagnostics = self.signal_analyzer.analyze(
            audio_file
        )

        diagnostics_seconds = (
            time.perf_counter()
            - diagnostics_started
        )

        self._last_signal = diagnostics

        if not diagnostics.usable_for_stt:
            self._last_timing = STTTimingDiagnostics(
                calibration_seconds=calibration_seconds,
                capture_seconds=capture_seconds,
                diagnostics_seconds=diagnostics_seconds,
            )
            return ""

        normalization_started = time.perf_counter()

        normalized_audio = self._normalize_for_stt(
            audio_file
        )

        normalization_seconds = (
            time.perf_counter()
            - normalization_started
        )

        transcription_started = time.perf_counter()

        text = await self._transcribe(
            normalized_audio,
            language=language,
        )

        transcription_seconds = (
            time.perf_counter()
            - transcription_started
        )

        self._last_timing = STTTimingDiagnostics(
            calibration_seconds=calibration_seconds,
            capture_seconds=capture_seconds,
            diagnostics_seconds=diagnostics_seconds,
            normalization_seconds=normalization_seconds,
            transcription_seconds=transcription_seconds,
        )

        return text

    async def _transcribe(
        self,
        audio_file: str | Path,
        *,
        language: str,
    ) -> str:
        text = await self.stt.transcribe(
            audio_file=audio_file,
            language=language,
        )

        return text.strip()

    @staticmethod
    def _coerce_audio_path(
        audio: str | Path | AudioRecordingResult,
    ) -> Path:
        if isinstance(
            audio,
            AudioRecordingResult,
        ):
            return audio.path

        return Path(
            audio
        )