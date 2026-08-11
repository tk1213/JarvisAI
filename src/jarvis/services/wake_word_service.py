from __future__ import annotations

import asyncio
import math
import queue
from collections.abc import Callable

import numpy as np
import sounddevice as sd
from pyopen_wakeword import (
    Model,
    OpenWakeWord,
    OpenWakeWordFeatures,
)
from scipy.signal import resample_poly

from jarvis.audio.manager import AudioManager


class WakeWordService:
    def __init__(
        self,
        *,
        audio: AudioManager | None = None,
        threshold: float = 0.50,
        model: Model = Model.HEY_JARVIS,
        wake_sample_rate: int = 16000,
        wake_frame_samples: int = 160,
    ) -> None:
        if not 0.0 < threshold <= 1.0:
            raise ValueError(
                "Wake word threshold must be "
                "between 0 and 1."
            )

        if wake_sample_rate <= 0:
            raise ValueError(
                "wake_sample_rate must be "
                "greater than zero."
            )

        if wake_frame_samples <= 0:
            raise ValueError(
                "wake_frame_samples must be "
                "greater than zero."
            )

        self._audio = (
            audio
            if audio is not None
            else AudioManager()
        )

        self._threshold = threshold
        self._model_type = model
        self._wake_sample_rate = wake_sample_rate
        self._wake_frame_samples = wake_frame_samples

        self._features = OpenWakeWordFeatures.from_builtin()
        self._wake_word = OpenWakeWord.from_builtin(
            self._model_type
        )

        self._closed = False

    @property
    def audio(self) -> AudioManager:
        return self._audio

    @property
    def threshold(self) -> float:
        return self._threshold

    @property
    def model_name(self) -> str:
        return self._model_type.value

    @property
    def closed(self) -> bool:
        return self._closed

    async def wait_for_wake_word(
        self,
        *,
        on_score: Callable[[float], None] | None = None,
    ) -> float:
        if self._closed:
            raise RuntimeError(
                "WakeWordService is closed."
            )

        self.reset()

        input_rate = self._audio.input_info.default_sample_rate
        input_device = self._audio.input_device

        audio_queue: queue.Queue[np.ndarray] = queue.Queue()

        pcm_buffer = np.empty(
            0,
            dtype=np.int16,
        )

        gcd = math.gcd(
            input_rate,
            self._wake_sample_rate,
        )

        up = self._wake_sample_rate // gcd
        down = input_rate // gcd

        def callback(
            indata: np.ndarray,
            frames: int,
            time_info: object,
            status: sd.CallbackFlags,
        ) -> None:
            del frames
            del time_info
            del status

            audio_queue.put(
                np.asarray(
                    indata[:, 0],
                    dtype=np.float32,
                ).copy()
            )

        with sd.InputStream(
            samplerate=input_rate,
            blocksize=0,
            dtype="float32",
            channels=1,
            device=input_device,
            latency="high",
            callback=callback,
        ):
            while not self._closed:
                try:
                    native_chunk = await asyncio.to_thread(
                        audio_queue.get,
                        True,
                        0.25,
                    )

                except queue.Empty:
                    await asyncio.sleep(
                        0
                    )
                    continue

                resampled = resample_poly(
                    native_chunk,
                    up=up,
                    down=down,
                )

                resampled = np.asarray(
                    resampled,
                    dtype=np.float32,
                )

                resampled = np.clip(
                    resampled,
                    -1.0,
                    1.0,
                )

                pcm16 = (
                    resampled
                    * 32767.0
                ).astype(
                    np.int16
                )

                pcm_buffer = np.concatenate(
                    (
                        pcm_buffer,
                        pcm16,
                    )
                )

                while len(pcm_buffer) >= self._wake_frame_samples:
                    frame = pcm_buffer[
                        : self._wake_frame_samples
                    ]

                    pcm_buffer = pcm_buffer[
                        self._wake_frame_samples :
                    ]

                    embeddings_iter = self._features.process_streaming(
                        frame.tobytes()
                    )

                    for embeddings in embeddings_iter:
                        scores = self._wake_word.process_streaming(
                            embeddings
                        )

                        for score in scores:
                            current_score = float(
                                score
                            )

                            if on_score is not None:
                                on_score(
                                    current_score
                                )

                            if current_score >= self._threshold:
                                return current_score

        if self._closed:
            raise RuntimeError(
                "WakeWordService was closed "
                "while waiting for wake word."
            )

        raise RuntimeError(
            "Wake word listener stopped unexpectedly."
        )

    def reset(self) -> None:
        if self._closed:
            return

        self._features.reset()
        self._wake_word.reset()

    def close(self) -> None:
        if self._closed:
            return

        self._features.close()
        self._wake_word.close()

        self._closed = True
