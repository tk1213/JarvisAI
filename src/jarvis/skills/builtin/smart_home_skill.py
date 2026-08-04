from __future__ import annotations

from typing import Any

from jarvis.services.capability import CapabilityDefinition
from jarvis.skills.base import Skill
from jarvis.skills.context import SkillContext
from jarvis.skills.metadata import SkillMetadata
from jarvis.smart_home.device import SmartDevice
from jarvis.smart_home.resolver import DeviceResolver


class SmartHomeSkill(Skill):
    def __init__(
        self,
        context: SkillContext,
    ) -> None:
        super().__init__()

        self.context = context
        self._device_resolver = DeviceResolver(
            smart_home=context.smart_home,
        )

    @property
    def metadata(self) -> SkillMetadata:
        return SkillMetadata(
            name="smart_home",
            version="1.0.0",
            description="Built-in smart home controls",
            capabilities=[
                "smart_home.list_devices",
                "smart_home.status",
                "smart_home.turn_on",
                "smart_home.turn_off",
                "smart_home.toggle",
            ],
            priority=1,
        )

    @property
    def capability_definitions(
        self,
    ) -> list[CapabilityDefinition]:
        device_query_argument = {
            "device_query": (
                "Natural-language device description from the user, "
                "such as 'ไฟห้องนั่งเล่น', 'bedroom light', "
                "or 'garage door'. Do not invent a device ID."
            ),
        }

        return [
            CapabilityDefinition(
                name="smart_home.list_devices",
                description=(
                    "List all smart home devices currently "
                    "available to JarvisAI."
                ),
            ),
            CapabilityDefinition(
                name="smart_home.status",
                description=(
                    "Get the current status of a smart home device."
                ),
                arguments=device_query_argument,
            ),
            CapabilityDefinition(
                name="smart_home.turn_on",
                description=(
                    "Turn on a smart home device."
                ),
                arguments=device_query_argument,
            ),
            CapabilityDefinition(
                name="smart_home.turn_off",
                description=(
                    "Turn off a smart home device."
                ),
                arguments=device_query_argument,
            ),
            CapabilityDefinition(
                name="smart_home.toggle",
                description=(
                    "Toggle the power state of a smart home device."
                ),
                arguments=device_query_argument,
            ),
        ]

    async def execute(
        self,
        command: str,
        **kwargs: Any,
    ) -> Any:
        smart_home = self.context.smart_home

        if command == "smart_home.list_devices":
            devices = await smart_home.list_devices()

            return [
                self._serialize_device(device)
                for device in devices
            ]

        device = await self._resolve_device(
            kwargs,
        )

        if device is None:
            result: dict[str, Any] = {
                "success": False,
                "error": "device_not_found",
            }

            device_id = kwargs.get("device_id")

            if isinstance(device_id, str):
                result["device_id"] = device_id.strip()

            device_query = kwargs.get("device_query")

            if isinstance(device_query, str):
                result["device_query"] = device_query.strip()

            return result

        if command == "smart_home.status":
            return {
                "success": True,
                "device": self._serialize_device(
                    device
                ),
            }

        if command == "smart_home.turn_on":
            success = await smart_home.turn_on(
                device.id
            )

            return {
                "success": success,
                "device_id": device.id,
                "device_name": device.name,
                "power": True if success else None,
            }

        if command == "smart_home.turn_off":
            success = await smart_home.turn_off(
                device.id
            )

            return {
                "success": success,
                "device_id": device.id,
                "device_name": device.name,
                "power": False if success else None,
            }

        if command == "smart_home.toggle":
            success = await smart_home.toggle(
                device.id
            )

            if not success:
                return {
                    "success": False,
                    "device_id": device.id,
                    "device_name": device.name,
                }

            updated_device = await smart_home.get_device(
                device.id
            )

            return {
                "success": True,
                "device_id": device.id,
                "device_name": device.name,
                "power": (
                    updated_device.power
                    if updated_device is not None
                    else None
                ),
            }

        raise ValueError(
            f"Unsupported command: {command}"
        )

    async def _resolve_device(
        self,
        arguments: dict[str, Any],
    ) -> SmartDevice | None:
        device_id = arguments.get(
            "device_id"
        )

        if device_id is not None:
            if not isinstance(
                device_id,
                str,
            ):
                raise TypeError(
                    "device_id must be a string."
                )

            device_id = device_id.strip()

            if not device_id:
                raise ValueError(
                    "device_id is required."
                )

            device = await self.context.smart_home.get_device(
                device_id
            )

            if device is not None:
                return device

        device_query = arguments.get(
            "device_query"
        )

        if device_query is None:
            if device_id is not None:
                return None

            raise ValueError(
                "device_query or device_id is required."
            )

        if not isinstance(
            device_query,
            str,
        ):
            raise TypeError(
                "device_query must be a string."
            )

        device_query = device_query.strip()

        if not device_query:
            raise ValueError(
                "device_query is required."
            )

        return await self._device_resolver.resolve(
            device_query
        )

    @staticmethod
    def _serialize_device(
        device: SmartDevice,
    ) -> dict[str, Any]:
        return {
            "id": device.id,
            "name": device.name,
            "room": device.room,
            "device_type": device.device_type,
            "online": device.online,
            "power": device.power,
        }