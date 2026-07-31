from __future__ import annotations

from abc import ABC, abstractmethod

from jarvis.smart_home.device import SmartDevice


class SmartHomeAdapter(ABC):
    """
    Base interface for all smart-home providers.

    Examples
    --------
    - Tuya
    - Home Assistant
    - MQTT
    - ESPHome
    - Mock Adapter
    """

    @abstractmethod
    async def connect(self) -> None:
        """Connect to the smart-home platform."""

    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from the smart-home platform."""

    @abstractmethod
    async def list_devices(self) -> list[SmartDevice]:
        """Return all available devices."""

    @abstractmethod
    async def turn_on(self, device_id: str) -> bool:
        """Turn a device on."""

    @abstractmethod
    async def turn_off(self, device_id: str) -> bool:
        """Turn a device off."""

    @abstractmethod
    async def toggle(self, device_id: str) -> bool:
        """Toggle a device."""

    @abstractmethod
    async def get_device(self, device_id: str) -> SmartDevice | None:
        """Return a single device."""