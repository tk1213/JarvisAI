from __future__ import annotations

from unittest.mock import AsyncMock, Mock

import pytest

from jarvis.smart_home.device import SmartDevice
from jarvis.smart_home.resolution import (
    DeviceResolutionStatus,
)
from jarvis.smart_home.resolver import DeviceResolver
from jarvis.smart_home.service import SmartHomeService


def make_device(
    device_id: str,
    name: str,
    *,
    room: str = "",
    device_type: str = "cz",
) -> SmartDevice:
    return SmartDevice(
        id=device_id,
        name=name,
        room=room,
        device_type=device_type,
        online=True,
        power=False,
    )


def make_resolver(
    devices: list[SmartDevice],
) -> DeviceResolver:
    smart_home = Mock(
        spec=SmartHomeService,
    )

    smart_home.list_devices = AsyncMock(
        return_value=devices,
    )

    return DeviceResolver(
        smart_home=smart_home,
    )


@pytest.mark.asyncio
async def test_detailed_found_by_exact_name() -> None:
    plug = make_device(
        "plug001",
        "Smart Plug",
    )

    resolver = make_resolver(
        [plug]
    )

    result = await resolver.resolve_detailed(
        "Smart Plug",
    )

    assert (
        result.status
        is DeviceResolutionStatus.FOUND
    )
    assert result.is_found
    assert result.device == plug
    assert result.candidates == (plug,)


@pytest.mark.asyncio
async def test_detailed_found_from_thai_stt_variant() -> None:
    plug = make_device(
        "plug001",
        "Smart Plug",
    )

    resolver = make_resolver(
        [plug]
    )

    result = await resolver.resolve_detailed(
        "เปิดสมาร์ทปลัก",
    )

    assert result.is_found
    assert result.device == plug


@pytest.mark.asyncio
async def test_detailed_not_found() -> None:
    plug = make_device(
        "plug001",
        "Smart Plug",
    )

    resolver = make_resolver(
        [plug]
    )

    result = await resolver.resolve_detailed(
        "เปิดเครื่องชงกาแฟ",
    )

    assert (
        result.status
        is DeviceResolutionStatus.NOT_FOUND
    )
    assert result.is_not_found
    assert result.device is None
    assert result.candidates == ()


@pytest.mark.asyncio
async def test_detailed_empty_text_is_not_found() -> None:
    resolver = make_resolver(
        []
    )

    result = await resolver.resolve_detailed(
        "   ",
    )

    assert result.is_not_found
    assert result.device is None
    assert result.candidates == ()


@pytest.mark.asyncio
async def test_detailed_generic_plug_is_ambiguous() -> None:
    living_room_plug = make_device(
        "plug001",
        "Living Room Smart Plug",
        room="Living Room",
    )

    bedroom_plug = make_device(
        "plug002",
        "Bedroom Smart Plug",
        room="Bedroom",
    )

    resolver = make_resolver(
        [
            living_room_plug,
            bedroom_plug,
        ]
    )

    result = await resolver.resolve_detailed(
        "เปิดปลัก",
    )

    assert (
        result.status
        is DeviceResolutionStatus.AMBIGUOUS
    )
    assert result.is_ambiguous
    assert result.device is None

    assert result.candidates == (
        living_room_plug,
        bedroom_plug,
    )


@pytest.mark.asyncio
async def test_detailed_exact_name_wins_over_ambiguity() -> None:
    living_room_plug = make_device(
        "plug001",
        "Living Room Smart Plug",
        room="Living Room",
    )

    bedroom_plug = make_device(
        "plug002",
        "Bedroom Smart Plug",
        room="Bedroom",
    )

    resolver = make_resolver(
        [
            living_room_plug,
            bedroom_plug,
        ]
    )

    result = await resolver.resolve_detailed(
        "Bedroom Smart Plug",
    )

    assert result.is_found
    assert result.device == bedroom_plug
    assert not result.is_ambiguous


@pytest.mark.asyncio
async def test_legacy_resolve_returns_none_for_ambiguity() -> None:
    first = make_device(
        "plug001",
        "Living Room Smart Plug",
        room="Living Room",
    )

    second = make_device(
        "plug002",
        "Bedroom Smart Plug",
        room="Bedroom",
    )

    resolver = make_resolver(
        [
            first,
            second,
        ]
    )

    device = await resolver.resolve(
        "เปิดปลั๊ก",
    )

    assert device is None