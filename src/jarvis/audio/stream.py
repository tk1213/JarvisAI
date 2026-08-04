from __future__ import annotations

from collections.abc import Generator

import sounddevice as sd

from jarvis.audio.manager import AudioManager


class AudioStream:
    def __init__(
        self,
        sample_rate: int | None = None,
        frame_duration_ms: int = 20,
    ) -> None:
        self.audio = AudioManager()

        self.sample_rate = (
            sample_rate
            if sample_rate is not None
            else self.audio.sample_rate
        )

        self.frame_duration_ms = frame_duration_ms

        self.frame_samples = (
            self.sample_rate
            * self.frame_duration_ms
            // 1000
        )

    def frames(
        self,
    ) -> Generator[bytes, None, None]:
        """
        Yield 16-bit mono PCM frames from the selected microphone.
        """

        with sd.RawInputStream(
            samplerate=self.sample_rate,
            blocksize=self.frame_samples,
            dtype="int16",
            channels=1,
            device=self.audio.input_device,
        ) as stream:
            while True:
                data, overflow = stream.read(
                    self.frame_samples
                )

                if overflow:
                    continue

                yield bytes(data)