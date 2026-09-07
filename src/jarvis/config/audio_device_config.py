from __future__ import annotations

from pathlib import Path

from dotenv import set_key, unset_key


class AudioDeviceConfig:
    INPUT_KEY = "AUDIO_INPUT_DEVICE"
    OUTPUT_KEY = "AUDIO_OUTPUT_DEVICE"

    def __init__(
        self,
        *,
        env_file: str | Path = ".env",
    ) -> None:
        self._env_file = Path(env_file)

    def set_input_device(
        self,
        device_index: int,
    ) -> None:
        set_key(
            str(self._env_file),
            self.INPUT_KEY,
            str(device_index),
            quote_mode="never",
        )

    def set_output_device(
        self,
        device_index: int,
    ) -> None:
        set_key(
            str(self._env_file),
            self.OUTPUT_KEY,
            str(device_index),
            quote_mode="never",
        )

    def reset_input_device(self) -> None:
        unset_key(
            str(self._env_file),
            self.INPUT_KEY,
        )

    def reset_output_device(self) -> None:
        unset_key(
            str(self._env_file),
            self.OUTPUT_KEY,
        )