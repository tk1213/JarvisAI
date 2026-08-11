from __future__ import annotations

import pytest

from jarvis.audio.device_selection import (
    AudioDeviceCatalog,
    AudioDeviceInfo,
    AudioDeviceKind,
)


def device(
    index: int,
    name: str,
    host_api: str,
    *,
    inputs: int = 0,
    outputs: int = 0,
) -> AudioDeviceInfo:
    return AudioDeviceInfo(
        index=index,
        name=name,
        host_api=host_api,
        max_input_channels=inputs,
        max_output_channels=outputs,
        default_sample_rate=48000,
    )


def test_prefers_wasapi_microphone() -> None:
    catalog = AudioDeviceCatalog(
        (
            device(
                0,
                "Generic Mic",
                "MME",
                inputs=1,
            ),
            device(
                1,
                "RODE Microphone",
                "Windows WASAPI",
                inputs=1,
            ),
        )
    )

    assert catalog.select_input().index == 1


def test_prefers_speakers_for_output() -> None:
    catalog = AudioDeviceCatalog(
        (
            device(
                0,
                "Digital Output",
                "Windows WASAPI",
                outputs=2,
            ),
            device(
                1,
                "Speakers Realtek",
                "Windows WASAPI",
                outputs=2,
            ),
        )
    )

    assert catalog.select_output().index == 1


def test_excludes_stereo_mix_for_input() -> None:
    catalog = AudioDeviceCatalog(
        (
            device(
                0,
                "Stereo Mix",
                "Windows WASAPI",
                inputs=2,
            ),
            device(
                1,
                "USB Microphone",
                "MME",
                inputs=1,
            ),
        )
    )

    assert catalog.select_input().index == 1


def test_manual_device_lookup_validates_kind() -> None:
    catalog = AudioDeviceCatalog(
        (
            device(
                3,
                "Speaker",
                "MME",
                outputs=2,
            ),
        )
    )

    with pytest.raises(
        ValueError,
        match="does not support input",
    ):
        catalog.get(
            3,
            kind=AudioDeviceKind.INPUT,
        )


def test_missing_input_device_fails_explicitly() -> None:
    catalog = AudioDeviceCatalog(
        (
            device(
                1,
                "Speaker",
                "MME",
                outputs=2,
            ),
        )
    )

    with pytest.raises(
        RuntimeError,
        match="No usable audio input",
    ):
        catalog.select_input()


def test_sounddevice_shape_is_normalized() -> None:
    catalog = AudioDeviceCatalog.from_sounddevice(
        devices=(
            {
                "name": "USB Mic",
                "hostapi": 0,
                "max_input_channels": 1,
                "max_output_channels": 0,
                "default_samplerate": 44100.0,
            },
        ),
        hostapis=(
            {
                "name": "Windows WASAPI",
            },
        ),
    )

    info = catalog.devices[0]

    assert info.index == 0
    assert info.name == "USB Mic"
    assert info.host_api == "Windows WASAPI"
    assert info.default_sample_rate == 44100
