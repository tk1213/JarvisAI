from __future__ import annotations

from pathlib import Path

from dotenv import set_key, unset_key


class AudioDeviceConfig:
    INPUT_KEY = "AUDIO_INPUT_DEVICE"
    INPUT_NAME_KEY = "AUDIO_INPUT_DEVICE_NAME"
    INPUT_HOST_API_KEY = "AUDIO_INPUT_DEVICE_HOST_API"

    OUTPUT_KEY = "AUDIO_OUTPUT_DEVICE"
    OUTPUT_NAME_KEY = "AUDIO_OUTPUT_DEVICE_NAME"
    OUTPUT_HOST_API_KEY = "AUDIO_OUTPUT_DEVICE_HOST_API"

    def __init__(
        self,
        *,
        env_file: str | Path = ".env",
    ) -> None:
        self._env_file = Path(env_file)

    @staticmethod
    def _validate_identity(
        *,
        name: str | None,
        host_api: str | None,
    ) -> None:
        if (name is None) != (host_api is None):
            raise ValueError(
                "Audio device identity requires both name and host API."
            )

    def set_input_device(
        self,
        device_index: int,
        *,
        name: str | None = None,
        host_api: str | None = None,
    ) -> None:
        self._validate_identity(
            name=name,
            host_api=host_api,
        )

        set_key(
            str(self._env_file),
            self.INPUT_KEY,
            str(device_index),
            quote_mode="never",
        )

        if name is not None and host_api is not None:
            set_key(
                str(self._env_file),
                self.INPUT_NAME_KEY,
                name,
                quote_mode="never",
            )
            set_key(
                str(self._env_file),
                self.INPUT_HOST_API_KEY,
                host_api,
                quote_mode="never",
            )

    def set_output_device(
        self,
        device_index: int,
        *,
        name: str | None = None,
        host_api: str | None = None,
    ) -> None:
        self._validate_identity(
            name=name,
            host_api=host_api,
        )

        set_key(
            str(self._env_file),
            self.OUTPUT_KEY,
            str(device_index),
            quote_mode="never",
        )

        if name is not None and host_api is not None:
            set_key(
                str(self._env_file),
                self.OUTPUT_NAME_KEY,
                name,
                quote_mode="never",
            )
            set_key(
                str(self._env_file),
                self.OUTPUT_HOST_API_KEY,
                host_api,
                quote_mode="never",
            )

    def reset_input_device(self) -> None:
        unset_key(
            str(self._env_file),
            self.INPUT_KEY,
        )
        unset_key(
            str(self._env_file),
            self.INPUT_NAME_KEY,
        )
        unset_key(
            str(self._env_file),
            self.INPUT_HOST_API_KEY,
        )

    def reset_output_device(self) -> None:
        unset_key(
            str(self._env_file),
            self.OUTPUT_KEY,
        )
        unset_key(
            str(self._env_file),
            self.OUTPUT_NAME_KEY,
        )
        unset_key(
            str(self._env_file),
            self.OUTPUT_HOST_API_KEY,
        )