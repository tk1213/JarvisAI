from __future__ import annotations

from unittest.mock import AsyncMock, Mock

import pytest

from jarvis.smart_home.device import SmartDevice
from jarvis.smart_home.mock_adapter import MockAdapter
from jarvis.smart_home.resolver import DeviceResolver
from jarvis.smart_home.service import SmartHomeService


@pytest.fixture
def resolver() -> DeviceResolver:
    smart_home = SmartHomeService(
        adapter=MockAdapter(),
    )

    return DeviceResolver(
        smart_home=smart_home,
    )


@pytest.fixture
def smart_plug_resolver() -> DeviceResolver:
    smart_home = Mock(
        spec=SmartHomeService,
    )

    smart_home.list_devices = AsyncMock(
        return_value=[
            SmartDevice(
                id="plug001",
                name="Smart Plug",
                room="Living Room",
                device_type="cz",
                online=True,
                power=False,
            ),
        ]
    )

    return DeviceResolver(
        smart_home=smart_home,
    )


@pytest.mark.asyncio
async def test_resolve_by_device_id(
    resolver: DeviceResolver,
) -> None:
    device = await resolver.resolve(
        "light001",
    )

    assert device is not None
    assert device.id == "light001"


@pytest.mark.asyncio
async def test_resolve_by_exact_device_name(
    resolver: DeviceResolver,
) -> None:
    device = await resolver.resolve(
        "Living Room Light",
    )

    assert device is not None
    assert device.id == "light001"


@pytest.mark.asyncio
async def test_resolve_device_name_case_insensitive(
    resolver: DeviceResolver,
) -> None:
    device = await resolver.resolve(
        "please turn on LIVING ROOM LIGHT",
    )

    assert device is not None
    assert device.id == "light001"


@pytest.mark.asyncio
async def test_resolve_thai_living_room_light(
    resolver: DeviceResolver,
) -> None:
    device = await resolver.resolve(
        "เปิดไฟห้องนั่งเล่นให้หน่อย",
    )

    assert device is not None
    assert device.id == "light001"


@pytest.mark.asyncio
async def test_resolve_thai_bedroom_light(
    resolver: DeviceResolver,
) -> None:
    device = await resolver.resolve(
        "ปิดไฟห้องนอน",
    )

    assert device is not None
    assert device.id == "light002"


@pytest.mark.asyncio
async def test_resolve_fan(
    resolver: DeviceResolver,
) -> None:
    device = await resolver.resolve(
        "เปิดพัดลมห้องนั่งเล่น",
    )

    assert device is not None
    assert device.id == "fan001"


@pytest.mark.asyncio
async def test_resolve_air_conditioner(
    resolver: DeviceResolver,
) -> None:
    device = await resolver.resolve(
        "เปิดแอร์ห้องนอน",
    )

    assert device is not None
    assert device.id == "ac001"


@pytest.mark.asyncio
async def test_resolve_garage_door(
    resolver: DeviceResolver,
) -> None:
    device = await resolver.resolve(
        "เปิดประตูโรงรถ",
    )

    assert device is not None
    assert device.id == "garage001"


@pytest.mark.asyncio
async def test_resolve_english_alias(
    resolver: DeviceResolver,
) -> None:
    device = await resolver.resolve(
        "turn on the bedroom light",
    )

    assert device is not None
    assert device.id == "light002"


@pytest.mark.asyncio
async def test_unknown_device_returns_none(
    resolver: DeviceResolver,
) -> None:
    device = await resolver.resolve(
        "เปิดเครื่องชงกาแฟ",
    )

    assert device is None


@pytest.mark.asyncio
async def test_empty_text_returns_none(
    resolver: DeviceResolver,
) -> None:
    device = await resolver.resolve(
        "   ",
    )

    assert device is None


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "spoken_text",
    [
        "สมาร์ทปลั๊ก",
        "สมาร์ทปลัก",
        "สมาร์ทพลั๊ก",
        "สมาร์ทพลัก",
        "สมาร์ท พลั๊ก",
        "สมาร์ท พลัก",
        "ปลั๊ก",
        "ปลัก",
        "ปลั๊กไฟ",
        "ปลักไฟ",
        "smart plug",
        "smartplug",
    ],
)
async def test_resolve_smart_plug_stt_variants(
    smart_plug_resolver: DeviceResolver,
    spoken_text: str,
) -> None:
    device = await smart_plug_resolver.resolve(
        spoken_text,
    )

    assert device is not None
    assert device.id == "plug001"
    assert device.name == "Smart Plug"


@pytest.mark.asyncio
async def test_resolve_smart_plug_variant_inside_command(
    smart_plug_resolver: DeviceResolver,
) -> None:
    device = await smart_plug_resolver.resolve(
        "ช่วยเปิดสมาร์ทปลักให้หน่อย",
    )

    assert device is not None
    assert device.id == "plug001"


@pytest.mark.asyncio
async def test_generic_plug_phrase_is_ambiguous_with_two_plugs() -> None:
    smart_home = Mock(
        spec=SmartHomeService,
    )

    smart_home.list_devices = AsyncMock(
        return_value=[
            SmartDevice(
                id="plug001",
                name="Living Room Smart Plug",
                room="Living Room",
                device_type="cz",
                online=True,
                power=False,
            ),
            SmartDevice(
                id="plug002",
                name="Bedroom Smart Plug",
                room="Bedroom",
                device_type="cz",
                online=True,
                power=False,
            ),
        ]
    )

    resolver = DeviceResolver(
        smart_home=smart_home,
    )

    device = await resolver.resolve(
        "เปิดปลัก",
    )

    assert device is None


@pytest.mark.asyncio
async def test_exact_name_wins_with_multiple_plugs() -> None:
    smart_home = Mock(
        spec=SmartHomeService,
    )

    smart_home.list_devices = AsyncMock(
        return_value=[
            SmartDevice(
                id="plug001",
                name="Living Room Smart Plug",
                room="Living Room",
                device_type="cz",
                online=True,
                power=False,
            ),
            SmartDevice(
                id="plug002",
                name="Bedroom Smart Plug",
                room="Bedroom",
                device_type="cz",
                online=True,
                power=False,
            ),
        ]
    )

    resolver = DeviceResolver(
        smart_home=smart_home,
    )

    device = await resolver.resolve(
        "Bedroom Smart Plug",
    )

    assert device is not None
    assert device.id == "plug002"