from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(
    slots=True,
    frozen=True,
)
class VoiceActivityResult:
    is_speech: bool
    rms: float


class VoiceActivityDetector:
    """
    Lightweight energy-based Voice Activity Detector.

    The detector receives raw 16-bit mono PCM frames and decides
    whether the frame likely contains speech based on RMS energy.

    This implementation has no additional external dependency.
    """

    def __init__(
        self,
        threshold: float = 500.0,
    ) -> None:
        if threshold <= 0:
            raise ValueError(
                "VAD threshold must be greater than zero."
            )

        self.threshold = threshold

    def analyze(
        self,
        frame: bytes,
    ) -> VoiceActivityResult:
        if not frame:
            return VoiceActivityResult(
                is_speech=False,
                rms=0.0,
            )

        samples = np.frombuffer(
            frame,
            dtype=np.int16,
        )

        if samples.size == 0:
            return VoiceActivityResult(
                is_speech=False,
                rms=0.0,
            )

        float_samples = samples.astype(
            np.float32
        )

        rms = float(
            np.sqrt(
                np.mean(
                    np.square(
                        float_samples
                    )
                )
            )
        )

        return VoiceActivityResult(
            is_speech=rms >= self.threshold,
            rms=rms,
        )

    def is_speech(
        self,
        frame: bytes,
    ) -> bool:
        return self.analyze(
            frame
        ).is_speech