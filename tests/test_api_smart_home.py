from __future__ import annotations

from unittest.mock import AsyncMock, Mock

import pytest
from httpx import ASGITransport, AsyncClient

from jarvis.api import create_api_app
from jarvis.smart_home.device import SmartDevice
from jarvis.smart_home.service import SmartHomeService


@pytest.mark.asyncio
async def test_lists_smart_home_devices_read_only() -> None:
    smart_home = Mock(
        spec=SmartHomeService,
    )
    smart_home.connected = True
    smart_home.list_devices = AsyncMock(
        return_value=[
            SmartDevice(
                id="plug001",
                name="Smart Plug 1",
                room="Living Room",
                device_type="plug",
                online=True,
                power=True,
            ),
            SmartDevice(
                id="plug002",
                name="Smart plug 2",
                room="Bedroom",
                device_type="plug",
                online=False,
                power=False,
            ),
        ]
    )

    app = create_api_app(
        smart_home=smart_home,
    )

    transport = ASGITransport(
        app=app,
    )

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        response = await client.get(
            "/api/v1/smart-home/devices"
        )

    assert response.status_code == 200
    assert response.json() == {
        "connected": True,
        "devices": [
            {
                "id": "plug001",
                "name": "Smart Plug 1",
                "room": "Living Room",
                "device_type": "plug",
                "online": True,
                "power": True,
            },
            {
                "id": "plug002",
                "name": "Smart plug 2",
                "room": "Bedroom",
                "device_type": "plug",
                "online": False,
                "power": False,
            },
        ],
    }

    smart_home.list_devices.assert_awaited_once_with()
    smart_home.get_device.assert_not_awaited()
    smart_home.turn_on.assert_not_awaited()
    smart_home.turn_off.assert_not_awaited()
    smart_home.toggle.assert_not_awaited()


@pytest.mark.asyncio
async def test_lists_empty_devices_when_disconnected() -> None:
    smart_home = Mock(
        spec=SmartHomeService,
    )
    smart_home.connected = False
    smart_home.list_devices = AsyncMock(
        return_value=[],
    )

    app = create_api_app(
        smart_home=smart_home,
    )

    transport = ASGITransport(
        app=app,
    )

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        response = await client.get(
            "/api/v1/smart-home/devices"
        )

    assert response.status_code == 200
    assert response.json() == {
        "connected": False,
        "devices": [],
    }

    smart_home.list_devices.assert_awaited_once_with()
    smart_home.get_device.assert_not_awaited()
    smart_home.turn_on.assert_not_awaited()
    smart_home.turn_off.assert_not_awaited()
    smart_home.toggle.assert_not_awaited()