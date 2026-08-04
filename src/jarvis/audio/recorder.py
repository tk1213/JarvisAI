from __future__ import annotations

import queue
import time
from collections import deque
from pathlib import Path

import numpy as np
import sounddevice as sd
import soundfile as sf

from jarvis.audio.manager import AudioManager
from jarvis.audio.vad import VoiceActivityDetector


class AudioRecorder:
    def __init__(self) -> None:
        self.audio = AudioManager()

    def record(
        self,
        seconds: float = 5.0,
        output: str = "record.wav",
    ) -> Path:
        """
        Record audio for a fixed duration.

        Kept for backward compatibility and fallback use.
        """

        output_path = Path(
            output
        ).resolve()

        print(
            f"Recording {seconds:.1f} seconds..."
        )

        recording = sd.rec(
            int(
                seconds
                * self.audio.sample_rate
            ),
            samplerate=self.audio.sample_rate,
            channels=self.audio.channels,
            dtype="float32",
            device=self.audio.input_device,
        )

        sd.wait()

        sf.write(
            output_path,
            recording,
            self.audio.sample_rate,
        )

        print("Recording finished.")

        return output_path

    def record_until_silence(
        self,
        output: str = "record.wav",
        *,
        threshold: float = 100.0,
        vad_frame_duration_ms: int = 20,
        speech_trigger_ms: int = 60,
        silence_duration_ms: int = 900,
        pre_roll_ms: int = 300,
        max_wait_seconds: float = 10.0,
        max_record_seconds: float = 15.0,
    ) -> Path | None:
        """
        Record using callback-based native audio streaming.

        Audio capture:
            sounddevice InputStream callback
            blocksize=0
            float32

        VAD:
            Native callback chunks are buffered in Python
            and analyzed in fixed-size VAD frames.

        Returns:
            Path when speech was recorded.
            None when no speech was detected.
        """

        self._validate_vad_settings(
            threshold=threshold,
            vad_frame_duration_ms=vad_frame_duration_ms,
            speech_trigger_ms=speech_trigger_ms,
            silence_duration_ms=silence_duration_ms,
            pre_roll_ms=pre_roll_ms,
            max_wait_seconds=max_wait_seconds,
            max_record_seconds=max_record_seconds,
        )

        output_path = Path(
            output
        ).resolve()

        sample_rate = self.audio.sample_rate

        vad_frame_samples = (
            sample_rate
            * vad_frame_duration_ms
            // 1000
        )

        speech_trigger_frames = max(
            1,
            speech_trigger_ms
            // vad_frame_duration_ms,
        )

        silence_frames_required = max(
            1,
            silence_duration_ms
            // vad_frame_duration_ms,
        )

        pre_roll_frames = max(
            1,
            pre_roll_ms
            // vad_frame_duration_ms,
        )

        vad = VoiceActivityDetector(
            threshold=threshold,
        )

        audio_queue: queue.Queue[np.ndarray] = (
            queue.Queue()
        )

        pre_roll: deque[np.ndarray] = deque(
            maxlen=pre_roll_frames
        )

        recorded_frames: list[np.ndarray] = []

        vad_buffer = np.empty(
            0,
            dtype=np.float32,
        )

        speech_started = False

        consecutive_speech_frames = 0
        consecutive_silence_frames = 0

        wait_started_at = time.monotonic()
        recording_started_at: float | None = None

        stream_status: list[str] = []

        def callback(
            indata: np.ndarray,
            frames: int,
            time_info: object,
            status: sd.CallbackFlags,
        ) -> None:
            del frames
            del time_info

            if status:
                stream_status.append(
                    str(status)
                )

            audio_queue.put(
                np.asarray(
                    indata[:, 0],
                    dtype=np.float32,
                ).copy()
            )

        print()
        print("Waiting for speech...")

        with sd.InputStream(
            samplerate=sample_rate,
            blocksize=0,
            dtype="float32",
            channels=1,
            device=self.audio.input_device,
            latency="high",
            callback=callback,
        ):
            while True:
                try:
                    native_chunk = audio_queue.get(
                        timeout=0.1
                    )
                except queue.Empty:
                    if not speech_started:
                        waited = (
                            time.monotonic()
                            - wait_started_at
                        )

                        if waited >= max_wait_seconds:
                            print(
                                "No speech detected."
                            )

                            return None

                    continue

                vad_buffer = np.concatenate(
                    (
                        vad_buffer,
                        native_chunk,
                    )
                )

                while (
                    len(vad_buffer)
                    >= vad_frame_samples
                ):
                    vad_frame = vad_buffer[
                        :vad_frame_samples
                    ]

                    vad_buffer = vad_buffer[
                        vad_frame_samples:
                    ]

                    pcm16 = self._float32_to_pcm16(
                        vad_frame
                    )

                    result = vad.analyze(
                        pcm16
                    )

                    if not speech_started:
                        pre_roll.append(
                            vad_frame.copy()
                        )

                        if result.is_speech:
                            consecutive_speech_frames += 1
                        else:
                            consecutive_speech_frames = 0

                        if (
                            consecutive_speech_frames
                            >= speech_trigger_frames
                        ):
                            speech_started = True

                            recording_started_at = (
                                time.monotonic()
                            )

                            recorded_frames.extend(
                                list(pre_roll)
                            )

                            pre_roll.clear()

                            print(
                                "Speech detected. Recording..."
                            )

                        continue

                    recorded_frames.append(
                        vad_frame.copy()
                    )

                    if result.is_speech:
                        consecutive_silence_frames = 0
                    else:
                        consecutive_silence_frames += 1

                    if (
                        consecutive_silence_frames
                        >= silence_frames_required
                    ):
                        print(
                            "Silence detected. "
                            "Recording finished."
                        )

                        recording = self._build_recording(
                            recorded_frames
                        )

                        self._write_recording(
                            output_path=output_path,
                            recording=recording,
                            sample_rate=sample_rate,
                        )

                        self._print_recording_summary(
                            recording=recording,
                            sample_rate=sample_rate,
                            stream_status=stream_status,
                        )

                        return output_path

                    if recording_started_at is not None:
                        recorded_seconds = (
                            time.monotonic()
                            - recording_started_at
                        )

                        if (
                            recorded_seconds
                            >= max_record_seconds
                        ):
                            print(
                                "Maximum recording duration "
                                "reached."
                            )

                            recording = (
                                self._build_recording(
                                    recorded_frames
                                )
                            )

                            self._write_recording(
                                output_path=output_path,
                                recording=recording,
                                sample_rate=sample_rate,
                            )

                            self._print_recording_summary(
                                recording=recording,
                                sample_rate=sample_rate,
                                stream_status=stream_status,
                            )

                            return output_path

                if not speech_started:
                    waited = (
                        time.monotonic()
                        - wait_started_at
                    )

                    if waited >= max_wait_seconds:
                        print(
                            "No speech detected."
                        )

                        return None

    @staticmethod
    def _build_recording(
        frames: list[np.ndarray],
    ) -> np.ndarray:
        if not frames:
            return np.empty(
                0,
                dtype=np.float32,
            )

        return np.concatenate(
            frames
        ).astype(
            np.float32,
            copy=False,
        )

    @staticmethod
    def _write_recording(
        *,
        output_path: Path,
        recording: np.ndarray,
        sample_rate: int,
    ) -> None:
        sf.write(
            output_path,
            recording,
            sample_rate,
        )

    @staticmethod
    def _print_recording_summary(
        *,
        recording: np.ndarray,
        sample_rate: int,
        stream_status: list[str],
    ) -> None:
        duration = (
            len(recording)
            / sample_rate
            if sample_rate > 0
            else 0.0
        )

        print(
            f"Recorded duration: "
            f"{duration:.2f} seconds"
        )

        if stream_status:
            print(
                f"Audio stream warnings: "
                f"{len(stream_status)}"
            )

            for message in stream_status:
                print(
                    f" - {message}"
                )

    @staticmethod
    def _float32_to_pcm16(
        frame: np.ndarray,
    ) -> bytes:
        clipped = np.clip(
            frame,
            -1.0,
            1.0,
        )

        pcm16 = (
            clipped
            * 32767.0
        ).astype(
            np.int16
        )

        return pcm16.tobytes()

    @staticmethod
    def _validate_vad_settings(
        *,
        threshold: float,
        vad_frame_duration_ms: int,
        speech_trigger_ms: int,
        silence_duration_ms: int,
        pre_roll_ms: int,
        max_wait_seconds: float,
        max_record_seconds: float,
    ) -> None:
        if threshold <= 0:
            raise ValueError(
                "threshold must be "
                "greater than zero."
            )

        if vad_frame_duration_ms <= 0:
            raise ValueError(
                "vad_frame_duration_ms must be "
                "greater than zero."
            )

        if speech_trigger_ms <= 0:
            raise ValueError(
                "speech_trigger_ms must be "
                "greater than zero."
            )

        if silence_duration_ms <= 0:
            raise ValueError(
                "silence_duration_ms must be "
                "greater than zero."
            )

        if pre_roll_ms <= 0:
            raise ValueError(
                "pre_roll_ms must be "
                "greater than zero."
            )

        if max_wait_seconds <= 0:
            raise ValueError(
                "max_wait_seconds must be "
                "greater than zero."
            )

        if max_record_seconds <= 0:
            raise ValueError(
                "max_record_seconds must be "
                "greater than zero."
            )