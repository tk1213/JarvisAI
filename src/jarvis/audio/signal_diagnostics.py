from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

import numpy as np
import soundfile as sf


class AudioSignalStatus(StrEnum):
    SILENT = "silent"
    LOW = "low"
    NORMAL = "normal"
    CLIPPING = "clipping"


@dataclass(slots=True, frozen=True)
class AudioSignalDiagnostics:
    path: Path
    sample_rate: int
    frames: int
    channels: int
    rms: float
    peak: float
    status: AudioSignalStatus

    @property
    def usable_for_stt(self) -> bool:
        return self.status in {
            AudioSignalStatus.LOW,
            AudioSignalStatus.NORMAL,
        }


class AudioSignalAnalyzer:
    """Analyze recorded audio before sending it to STT."""

    def __init__(
        self,
        *,
        silence_rms_threshold: float = 0.003,
        low_rms_threshold: float = 0.015,
        clipping_peak_threshold: float = 0.98,
    ) -> None:
        if silence_rms_threshold < 0:
            raise ValueError(
                "silence_rms_threshold cannot be negative."
            )

        if low_rms_threshold <= silence_rms_threshold:
            raise ValueError(
                "low_rms_threshold must be greater than "
                "silence_rms_threshold."
            )

        if not 0 < clipping_peak_threshold <= 1:
            raise ValueError(
                "clipping_peak_threshold must be between 0 and 1."
            )

        self._silence_rms_threshold = silence_rms_threshold
        self._low_rms_threshold = low_rms_threshold
        self._clipping_peak_threshold = clipping_peak_threshold

    def analyze(
        self,
        path: str | Path,
    ) -> AudioSignalDiagnostics:
        audio_path = Path(
            path
        )

        data, sample_rate = sf.read(
            audio_path,
            dtype="float32",
            always_2d=True,
        )

        array = np.asarray(
            data,
            dtype=np.float32,
        )

        frames = int(
            array.shape[0]
        )
        channels = int(
            array.shape[1]
        )

        if frames == 0:
            rms = 0.0
            peak = 0.0
        else:
            rms = float(
                np.sqrt(
                    np.mean(
                        np.square(
                            array,
                            dtype=np.float64,
                        )
                    )
                )
            )
            peak = float(
                np.max(
                    np.abs(
                        array
                    )
                )
            )

        status = self._classify(
            rms=rms,
            peak=peak,
        )

        return AudioSignalDiagnostics(
            path=audio_path,
            sample_rate=int(
                sample_rate
            ),
            frames=frames,
            channels=channels,
            rms=rms,
            peak=peak,
            status=status,
        )

    def _classify(
        self,
        *,
        rms: float,
        peak: float,
    ) -> AudioSignalStatus:
        if peak >= self._clipping_peak_threshold:
            return AudioSignalStatus.CLIPPING

        if rms <= self._silence_rms_threshold:
            return AudioSignalStatus.SILENT

        if rms < self._low_rms_threshold:
            return AudioSignalStatus.LOW

        return AudioSignalStatus.NORMAL
