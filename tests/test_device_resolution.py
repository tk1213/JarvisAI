from __future__ import annotations

import pytest

from jarvis.smart_home.device import SmartDevice
from jarvis.smart_home.resolution import (
    DeviceResolution,
    DeviceResolutionStatus,
)


def make_device(
    device_id: str,
    name: str,
) -> SmartDevice:
    return SmartDevice(
        id=device_id,
        name=name,
        room="",
        device_type="cz",
        online=True,
        power=False,
    )


def test_found_resolution() -> None:
    device = make_device(
        "plug001",
        "Living Room Smart Plug",
    )

    result = DeviceResolution.found(
        device
    )

    assert (
        result.status
        is DeviceResolutionStatus.FOUND
    )
    assert result.is_found
    assert not result.is_not_found
    assert not result.is_ambiguous

    assert result.device == device
    assert result.candidates == (device,)


def test_not_found_resolution() -> None:
    result = DeviceResolution.not_found()

    assert (
        result.status
        is DeviceResolutionStatus.NOT_FOUND
    )
    assert result.is_not_found
    assert not result.is_found
    assert not result.is_ambiguous

    assert result.device is None
    assert result.candidates == ()


def test_ambiguous_resolution() -> None:
    first = make_device(
        "plug001",
        "Living Room Smart Plug",
    )

    second = make_device(
        "plug002",
        "Bedroom Smart Plug",
    )

    result = DeviceResolution.ambiguous(
        [
            first,
            second,
        ]
    )

    assert (
        result.status
        is DeviceResolutionStatus.AMBIGUOUS
    )
    assert result.is_ambiguous
    assert not result.is_found
    assert not result.is_not_found

    assert result.device is None
    assert result.candidates == (
        first,
        second,
    )


def test_ambiguous_requires_multiple_devices() -> None:
    device = make_device(
        "plug001",
        "Smart Plug",
    )

    with pytest.raises(
        ValueError,
        match="at least two devices",
    ):
        DeviceResolution.ambiguous(
            [device]
        )