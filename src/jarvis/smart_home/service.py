from __future__ import annotations

from jarvis.smart_home.adapter import SmartHomeAdapter
from jarvis.smart_home.device import SmartDevice


class SmartHomeService:
    """
    High-level Smart Home business logic.
    """

    def __init__(
        self,
        adapter: SmartHomeAdapter,
    ) -> None:
        self._adapter = adapter
        self._connected = False

    @property
    def connected(self) -> bool:
        return self._connected

    async def connect(self) -> None:
        await self._adapter.connect()
        self._connected = True

    async def disconnect(self) -> None:
        try:
            await self._adapter.disconnect()
        finally:
            self._connected = False

    async def list_devices(
        self,
    ) -> list[SmartDevice]:
        return await self._adapter.list_devices()

    async def get_device(
        self,
        device_id: str,
    ) -> SmartDevice | None:
        return await self._adapter.get_device(
            device_id
        )

    async def turn_on(
        self,
        device_id: str,
    ) -> bool:
        return await self._adapter.turn_on(
            device_id
        )

    async def turn_off(
        self,
        device_id: str,
    ) -> bool:
        return await self._adapter.turn_off(
            device_id
        )

    async def toggle(
        self,
        device_id: str,
    ) -> bool:
        return await self._adapter.toggle(
            device_id
        )

    
