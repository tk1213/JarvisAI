from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from jarvis.audio.device_selection import (
    AudioDeviceCatalog,
    AudioDeviceInfo,
    AudioDeviceKind,
    AudioDeviceSelection,
)


@dataclass(slots=True, frozen=True)
class AudioManagerSnapshot:
    input_device: AudioDeviceInfo
    output_device: AudioDeviceInfo


class AudioManager:
    """Production audio-device manager with explicit and automatic selection."""

    def __init__(
        self,
        *,
        sounddevice_module: Any | None = None,
        input_device: int | None = None,
        output_device: int | None = None,
        input_device_name: str | None = None,
        input_device_host_api: str | None = None,
        output_device_name: str | None = None,
        output_device_host_api: str | None = None,
    ) -> None:
        if sounddevice_module is None:
            import sounddevice as sounddevice_module

        self._sounddevice = sounddevice_module
        self._catalog = self._build_catalog()

        automatic = self._catalog.select()

        self._input = self._resolve_initial_device(
            kind=AudioDeviceKind.INPUT,
            index=input_device,
            name=input_device_name,
            host_api=input_device_host_api,
            automatic=automatic.input_device,
        )
        self._output = self._resolve_initial_device(
            kind=AudioDeviceKind.OUTPUT,
            index=output_device,
            name=output_device_name,
            host_api=output_device_host_api,
            automatic=automatic.output_device,
        )

    @property
    def input_device(self) -> int:
        return self._input.index

    @property
    def output_device(self) -> int:
        return self._output.index

    @property
    def input_info(self) -> AudioDeviceInfo:
        return self._input

    @property
    def output_info(self) -> AudioDeviceInfo:
        return self._output

    @property
    def selection(self) -> AudioDeviceSelection:
        return AudioDeviceSelection(
            input_device=self._input,
            output_device=self._output,
        )

    @property
    def snapshot(self) -> AudioManagerSnapshot:
        return AudioManagerSnapshot(
            input_device=self._input,
            output_device=self._output,
        )

    def refresh(self) -> AudioManagerSnapshot:
        catalog = self._build_catalog()

        input_device = catalog.get(
            self._input.index,
            kind=AudioDeviceKind.INPUT,
        )
        output_device = catalog.get(
            self._output.index,
            kind=AudioDeviceKind.OUTPUT,
        )

        self._catalog = catalog
        self._input = input_device
        self._output = output_device

        return self.snapshot

    def select_input(
        self,
        device_index: int,
    ) -> AudioDeviceInfo:
        self._input = self._catalog.get(
            device_index,
            kind=AudioDeviceKind.INPUT,
        )
        return self._input

    def select_output(
        self,
        device_index: int,
    ) -> AudioDeviceInfo:
        self._output = self._catalog.get(
            device_index,
            kind=AudioDeviceKind.OUTPUT,
        )
        return self._output

    def input_devices(
        self,
    ) -> tuple[AudioDeviceInfo, ...]:
        return self._catalog.input_devices()

    def output_devices(
        self,
    ) -> tuple[AudioDeviceInfo, ...]:
        return self._catalog.output_devices()

    def _resolve_initial_device(
        self,
        *,
        kind: AudioDeviceKind,
        index: int | None,
        name: str | None,
        host_api: str | None,
        automatic: AudioDeviceInfo,
    ) -> AudioDeviceInfo:
        if name is not None or host_api is not None:
            if name is None or host_api is None:
                raise ValueError(
                    "Audio device identity requires both name and host API."
                )

            return self._catalog.get_by_identity(
                name=name,
                host_api=host_api,
                kind=kind,
            )

        if index is not None:
            return self._catalog.get(
                index,
                kind=kind,
            )

        return automatic

    def _build_catalog(
        self,
    ) -> AudioDeviceCatalog:
        return AudioDeviceCatalog.from_sounddevice(
            devices=self._sounddevice.query_devices(),
            hostapis=self._sounddevice.query_hostapis(),
        )
