from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class AudioDeviceKind(StrEnum):
    INPUT = "input"
    OUTPUT = "output"


@dataclass(slots=True, frozen=True)
class AudioDeviceInfo:
    index: int
    name: str
    host_api: str
    max_input_channels: int
    max_output_channels: int
    default_sample_rate: int

    def supports(
        self,
        kind: AudioDeviceKind,
    ) -> bool:
        if kind is AudioDeviceKind.INPUT:
            return self.max_input_channels > 0

        return self.max_output_channels > 0


@dataclass(slots=True, frozen=True)
class AudioDeviceSelection:
    input_device: AudioDeviceInfo
    output_device: AudioDeviceInfo


class AudioDeviceCatalog:
    """Pure device-selection logic independent from sounddevice."""

    INPUT_API_PRIORITY = (
        "Windows WASAPI",
        "Windows DirectSound",
        "MME",
        "Windows WDM-KS",
    )
    OUTPUT_API_PRIORITY = INPUT_API_PRIORITY

    INPUT_PREFERRED_NAMES = (
        "rode",
        "microphone",
        "mic",
    )
    OUTPUT_PREFERRED_NAMES = (
        "speakers",
        "headphones",
        "realtek",
    )

    INPUT_EXCLUDED_NAMES = (
        "stereo mix",
        "line in",
        "sound mapper",
        "primary sound capture",
    )
    OUTPUT_EXCLUDED_NAMES = (
        "digital output",
        "spdif",
        "display audio",
    )

    def __init__(
        self,
        devices: tuple[AudioDeviceInfo, ...],
    ) -> None:
        self._devices = devices

    @property
    def devices(self) -> tuple[AudioDeviceInfo, ...]:
        return self._devices

    @classmethod
    def from_sounddevice(
        cls,
        devices: Any,
        hostapis: Any,
    ) -> AudioDeviceCatalog:
        normalized: list[AudioDeviceInfo] = []

        for index, device in enumerate(devices):
            host_index = int(
                device["hostapi"]
            )
            host_api = str(
                hostapis[host_index]["name"]
            )

            normalized.append(
                AudioDeviceInfo(
                    index=index,
                    name=str(
                        device["name"]
                    ),
                    host_api=host_api,
                    max_input_channels=int(
                        device["max_input_channels"]
                    ),
                    max_output_channels=int(
                        device["max_output_channels"]
                    ),
                    default_sample_rate=int(
                        float(
                            device["default_samplerate"]
                        )
                    ),
                )
            )

        return cls(
            tuple(
                normalized
            )
        )

    def input_devices(
        self,
    ) -> tuple[AudioDeviceInfo, ...]:
        return tuple(
            device
            for device in self._devices
            if device.supports(
                AudioDeviceKind.INPUT
            )
        )

    def output_devices(
        self,
    ) -> tuple[AudioDeviceInfo, ...]:
        return tuple(
            device
            for device in self._devices
            if device.supports(
                AudioDeviceKind.OUTPUT
            )
        )

    def select(
        self,
    ) -> AudioDeviceSelection:
        return AudioDeviceSelection(
            input_device=self.select_input(),
            output_device=self.select_output(),
        )

    def select_input(
        self,
    ) -> AudioDeviceInfo:
        return self._select_best(
            kind=AudioDeviceKind.INPUT,
            api_priority=self.INPUT_API_PRIORITY,
            preferred_names=self.INPUT_PREFERRED_NAMES,
            excluded_names=self.INPUT_EXCLUDED_NAMES,
        )

    def select_output(
        self,
    ) -> AudioDeviceInfo:
        return self._select_best(
            kind=AudioDeviceKind.OUTPUT,
            api_priority=self.OUTPUT_API_PRIORITY,
            preferred_names=self.OUTPUT_PREFERRED_NAMES,
            excluded_names=self.OUTPUT_EXCLUDED_NAMES,
        )

    def get(
        self,
        index: int,
        *,
        kind: AudioDeviceKind | None = None,
    ) -> AudioDeviceInfo:
        for device in self._devices:
            if device.index != index:
                continue

            if (
                kind is not None
                and not device.supports(
                    kind
                )
            ):
                raise ValueError(
                    f"Audio device {index} does not support {kind.value}."
                )

            return device

        raise ValueError(
            f"Audio device {index} was not found."
        )

    def _select_best(
        self,
        *,
        kind: AudioDeviceKind,
        api_priority: tuple[str, ...],
        preferred_names: tuple[str, ...],
        excluded_names: tuple[str, ...],
    ) -> AudioDeviceInfo:
        usable = tuple(
            device
            for device in self._devices
            if device.supports(
                kind
            )
            and not self._excluded(
                device,
                excluded_names,
            )
        )

        for api_name in api_priority:
            for preferred_name in preferred_names:
                for device in usable:
                    if (
                        device.host_api == api_name
                        and preferred_name
                        in device.name.lower()
                    ):
                        return device

        if usable:
            return usable[0]

        raise RuntimeError(
            f"No usable audio {kind.value} device found."
        )

    @staticmethod
    def _excluded(
        device: AudioDeviceInfo,
        excluded_names: tuple[str, ...],
    ) -> bool:
        name = device.name.lower()

        return any(
            excluded in name
            for excluded in excluded_names
        )
