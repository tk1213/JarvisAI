from collections.abc import Callable
from pathlib import Path

import numpy as np
import sounddevice as sd
import soundfile as sf
from scipy.signal import resample_poly

from jarvis.audio.manager import AudioManager


class AudioPlayer:
    def __init__(
        self,
        audio: AudioManager | None = None,
    ) -> None:
        self.audio = (
            audio
            if audio is not None
            else AudioManager()
        )

    def play(
        self,
        filename: str | Path,
        blocking: bool = True,
        *,
        on_playback_start: Callable[[], None] | None = None,
    ) -> None:
        audio_path = Path(
            filename
        ).resolve()

        if not audio_path.exists():
            raise FileNotFoundError(
                f"Audio file not found: {audio_path}"
            )

        data, source_rate = sf.read(
            audio_path,
            dtype="float32",
            always_2d=False,
        )

        output_info = sd.query_devices(
            self.audio.output_device,
            kind="output",
        )

        target_rate = int(
            output_info["default_samplerate"]
        )

        if source_rate != target_rate:
            data = self._resample(
                data=data,
                source_rate=int(
                    source_rate
                ),
                target_rate=target_rate,
            )

        channels = (
            1
            if data.ndim == 1
            else int(
                data.shape[1]
            )
        )

        max_channels = int(
            output_info[
                "max_output_channels"
            ]
        )

        if channels > max_channels:
            raise RuntimeError(
                f"Audio has {channels} channels, "
                f"but output device supports only "
                f"{max_channels}."
            )

        print(
            f"Output device : "
            f"[{self.audio.output_device}] "
            f"{output_info['name']}"
        )
        print(
            f"Source rate   : {source_rate}"
        )
        print(
            f"Playback rate : {target_rate}"
        )
        print(
            f"Channels      : {channels}"
        )

        sd.check_output_settings(
            device=self.audio.output_device,
            samplerate=target_rate,
            channels=channels,
            dtype="float32",
        )

        if on_playback_start is not None:
            on_playback_start()

        sd.play(
            data=data,
            samplerate=target_rate,
            device=self.audio.output_device,
            blocking=blocking,
        )

    def stop(
        self,
    ) -> None:
        sd.stop()

    @staticmethod
    def _resample(
        data: np.ndarray,
        source_rate: int,
        target_rate: int,
    ) -> np.ndarray:
        common_divisor = np.gcd(
            source_rate,
            target_rate,
        )

        up = (
            target_rate
            // common_divisor
        )
        down = (
            source_rate
            // common_divisor
        )

        resampled = resample_poly(
            data,
            up=up,
            down=down,
            axis=0,
        )

        return np.asarray(
            resampled,
            dtype=np.float32,
        )
