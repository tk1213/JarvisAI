from __future__ import annotations

from jarvis.smart_home.mock_adapter import MockAdapter
from jarvis.smart_home.service import SmartHomeService


async def create_service() -> SmartHomeService:
    adapter = MockAdapter()
    await adapter.connect()
    return SmartHomeService(adapter)


async def test_list_devices():
    service = await create_service()

    devices = await service.list_devices()

    assert len(devices) == 5


async def test_turn_on():
    service = await create_service()

    assert await service.turn_on("light001") is True

    device = await service.get_device("light001")

    assert device is not None
    assert device.power is True


async def test_turn_off():
    service = await create_service()

    await service.turn_on("light001")

    assert await service.turn_off("light001") is True

    device = await service.get_device("light001")

    assert device is not None
    assert device.power is False


async def test_toggle():
    service = await create_service()

    device = await service.get_device("light001")

    assert device is not None
    assert device.power is False

    await service.toggle("light001")

    assert device.power is True

    await service.toggle("light001")

    assert device.power is False


async def test_unknown_device():
    service = await create_service()

    assert await service.turn_on("unknown") is False
    assert await service.get_device("unknown") is None