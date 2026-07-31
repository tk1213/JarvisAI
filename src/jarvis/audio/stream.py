from __future__ import annotations

from collections.abc import Generator

import sounddevice as sd

from jarvis.audio.manager import AudioManager


class AudioStream:
    def __init__(
        self,
        sample_rate: int = 16000,
        frame_duration_ms: int = 20,
    ) -> None:
        self.audio = AudioManager()

        self.sample_rate = sample_rate
        self.frame_duration_ms = frame_duration_ms

        self.frame_samples = (
            sample_rate * frame_duration_ms // 1000
        )

    def frames(self) -> Generator[bytes, None, None]:
        """
        Yield 16-bit mono PCM frames suitable for WebRTC VAD.
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