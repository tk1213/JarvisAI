from __future__ import annotations

from jarvis.smart_home.adapter import SmartHomeAdapter
from jarvis.smart_home.device import SmartDevice


class MockAdapter(SmartHomeAdapter):
    """
    In-memory Smart Home adapter for development and testing.
    """

    def __init__(self) -> None:
        self._devices: dict[str, SmartDevice] = {
            "light001": SmartDevice(
                id="light001",
                name="Living Room Light",
                room="Living Room",
                device_type="light",
            ),
            "light002": SmartDevice(
                id="light002",
                name="Bedroom Light",
                room="Bedroom",
                device_type="light",
            ),
            "fan001": SmartDevice(
                id="fan001",
                name="Living Room Fan",
                room="Living Room",
                device_type="fan",
            ),
            "ac001": SmartDevice(
                id="ac001",
                name="Bedroom Air Conditioner",
                room="Bedroom",
                device_type="air_conditioner",
            ),
            "garage001": SmartDevice(
                id="garage001",
                name="Garage Door",
                room="Garage",
                device_type="garage",
            ),
        }

    async def connect(self) -> None:
        return

    async def disconnect(self) -> None:
        return

    async def list_devices(self) -> list[SmartDevice]:
        return list(self._devices.values())

    async def get_device(
        self,
        device_id: str,
    ) -> SmartDevice | None:
        return self._devices.get(device_id)

    async def turn_on(
        self,
        device_id: str,
    ) -> bool:
        device = self._devices.get(device_id)

        if device is None:
            return False

        device.power = True
        return True

    async def turn_off(
        self,
        device_id: str,
    ) -> bool:
        device = self._devices.get(device_id)

        if device is None:
            return False

        device.power = False
        return True

    async def toggle(
        self,
        device_id: str,
    ) -> bool:
        device = self._devices.get(device_id)

        if device is None:
            return False

        device.power = not device.power
        return True