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
    ) -> None:
        if sounddevice_module is None:
            import sounddevice as sounddevice_module

        self._sounddevice = sounddevice_module
        self._catalog = self._build_catalog()

        automatic = self._catalog.select()

        self._input = (
            self._catalog.get(
                input_device,
                kind=AudioDeviceKind.INPUT,
            )
            if input_device is not None
            else automatic.input_device
        )
        self._output = (
            self._catalog.get(
                output_device,
                kind=AudioDeviceKind.OUTPUT,
            )
            if output_device is not None
            else automatic.output_device
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
        self._catalog = self._build_catalog()

        self._input = self._catalog.get(
            self._input.index,
            kind=AudioDeviceKind.INPUT,
        )
        self._output = self._catalog.get(
            self._output.index,
            kind=AudioDeviceKind.OUTPUT,
        )

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

    def _build_catalog(
        self,
    ) -> AudioDeviceCatalog:
        return AudioDeviceCatalog.from_sounddevice(
            devices=self._sounddevice.query_devices(),
            hostapis=self._sounddevice.query_hostapis(),
        )
