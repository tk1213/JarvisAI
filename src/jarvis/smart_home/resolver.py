from __future__ import annotations

import re

from jarvis.smart_home.device import SmartDevice
from jarvis.smart_home.resolution import DeviceResolution
from jarvis.smart_home.service import SmartHomeService
from jarvis.smart_home.text_normalizer import (
    SmartHomeTextNormalizer,
)


class DeviceResolver:
    def __init__(
        self,
        smart_home: SmartHomeService,
    ) -> None:
        self._smart_home = smart_home

    async def resolve(
        self,
        text: str,
    ) -> SmartDevice | None:
        """
        Backward-compatible device resolver.

        FOUND:
            Return the matched device.

        NOT_FOUND / AMBIGUOUS:
            Return None.
        """

        result = await self.resolve_detailed(
            text
        )

        return result.device

    async def resolve_detailed(
        self,
        text: str,
    ) -> DeviceResolution:
        normalized_text = self._normalize(
            text
        )

        if not normalized_text:
            return DeviceResolution.not_found()

        devices = await self._smart_home.list_devices()

        # -----------------------------------------------------
        # Exact device ID
        # -----------------------------------------------------
        for device in devices:
            if (
                self._normalize(device.id)
                == normalized_text
            ):
                return DeviceResolution.found(
                    device
                )

        # -----------------------------------------------------
        # Exact device name
        # -----------------------------------------------------
        for device in devices:
            if (
                self._normalize(device.name)
                == normalized_text
            ):
                return DeviceResolution.found(
                    device
                )

        # -----------------------------------------------------
        # Natural ordinal / number hint
        #
        # Examples:
        #   สมาร์ทปลั๊กสอง
        #   สมาร์ทปลั๊ก 2
        #   ปลั๊กตัวที่สอง
        #   ปลั๊กตัวที่ 2
        #   ปลั๊กเบอร์สอง
        #   ปลั๊กหมายเลข 2
        # -----------------------------------------------------
        requested_number = (
            self._extract_requested_number(
                normalized_text
            )
        )

        if requested_number is not None:
            numbered_matches = (
                self._find_numbered_device_matches(
                    text=normalized_text,
                    devices=devices,
                    number=requested_number,
                )
            )

            if len(numbered_matches) == 1:
                return DeviceResolution.found(
                    numbered_matches[0]
                )

            if len(numbered_matches) > 1:
                return DeviceResolution.ambiguous(
                    numbered_matches
                )

        # -----------------------------------------------------
        # Device name contained in user text
        # -----------------------------------------------------
        name_matches: list[SmartDevice] = []

        for device in devices:
            device_name = self._normalize(
                device.name
            )

            if (
                device_name
                and device_name in normalized_text
            ):
                name_matches.append(
                    device
                )

        name_matches = self._unique_devices(
            name_matches
        )

        if len(name_matches) == 1:
            return DeviceResolution.found(
                name_matches[0]
            )

        if len(name_matches) > 1:
            return DeviceResolution.ambiguous(
                name_matches
            )

        # -----------------------------------------------------
        # Known development-device aliases
        # -----------------------------------------------------
        development_matches = (
            self._find_development_alias_matches(
                normalized_text,
                devices,
            )
        )

        development_matches = self._unique_devices(
            development_matches
        )

        if len(development_matches) == 1:
            return DeviceResolution.found(
                development_matches[0]
            )

        if len(development_matches) > 1:
            return DeviceResolution.ambiguous(
                development_matches
            )

        # -----------------------------------------------------
        # Generic aliases based on device metadata
        # -----------------------------------------------------
        metadata_matches = (
            self._find_metadata_alias_matches(
                normalized_text,
                devices,
            )
        )

        metadata_matches = self._unique_devices(
            metadata_matches
        )

        if len(metadata_matches) == 1:
            return DeviceResolution.found(
                metadata_matches[0]
            )

        if len(metadata_matches) > 1:
            return DeviceResolution.ambiguous(
                metadata_matches
            )

        return DeviceResolution.not_found()

    @classmethod
    def _find_numbered_device_matches(
        cls,
        *,
        text: str,
        devices: list[SmartDevice],
        number: int,
    ) -> list[SmartDevice]:
        """
        Match an explicitly requested number against real device
        metadata before falling back to candidate position.

        Example:
            "สมาร์ทปลั๊กตัวที่สอง"
            -> prefer a device whose name is "Smart plug 2".
        """

        category_matches = (
            cls._find_metadata_alias_matches(
                text,
                devices,
            )
        )

        search_devices = (
            category_matches
            if category_matches
            else devices
        )

        matches: list[SmartDevice] = []

        for device in search_devices:
            if cls._device_matches_number(
                device,
                number,
            ):
                matches.append(
                    device
                )

        return cls._unique_devices(
            matches
        )

    @classmethod
    def _device_matches_number(
        cls,
        device: SmartDevice,
        number: int,
    ) -> bool:
        number_text = str(
            number
        )

        name = cls._normalize(
            device.name
        )

        device_id = cls._normalize(
            device.id
        )

        room = cls._normalize(
            device.room
        )

        if cls._contains_number_token(
            name,
            number_text,
        ):
            return True

        if cls._contains_number_token(
            device_id,
            number_text,
        ):
            return True

        return bool(
            room
            and cls._contains_number_token(
                room,
                number_text,
            )
        )

    @staticmethod
    def _contains_number_token(
        text: str,
        number: str,
    ) -> bool:
        pattern = (
            rf"(?<!\d){re.escape(number)}(?!\d)"
        )

        return bool(
            re.search(
                pattern,
                text,
            )
        )

    @classmethod
    def _extract_requested_number(
        cls,
        text: str,
    ) -> int | None:
        """
        Extract natural Thai/English device-number references.

        This intentionally supports only small ordinals used
        for device selection. It does not infer arbitrary numbers.
        """

        aliases: dict[int, tuple[str, ...]] = {
            1: (
                "ตัวแรก",
                "ตัวที่หนึ่ง",
                "ตัวที่ หนึ่ง",
                "ตัวที่ 1",
                "ตัว 1",
                "ตัวหนึ่ง",
                "อันแรก",
                "อันที่หนึ่ง",
                "อันที่ 1",
                "อันหนึ่ง",
                "เบอร์หนึ่ง",
                "เบอร์ 1",
                "หมายเลขหนึ่ง",
                "หมายเลข 1",
                "เครื่องแรก",
                "เครื่องที่หนึ่ง",
                "เครื่องที่ 1",
                "สมาร์ทปลั๊กหนึ่ง",
                "สมาร์ทปลั๊ก 1",
                "ปลั๊กหนึ่ง",
                "ปลั๊ก 1",
                "first",
                "number one",
            ),
            2: (
                "ตัวที่สอง",
                "ตัวที่ สอง",
                "ตัวที่ 2",
                "ตัว 2",
                "ตัวสอง",
                "อันที่สอง",
                "อันที่ 2",
                "อัน 2",
                "อันสอง",
                "เบอร์สอง",
                "เบอร์ 2",
                "หมายเลขสอง",
                "หมายเลข 2",
                "เครื่องที่สอง",
                "เครื่องที่ 2",
                "สมาร์ทปลั๊กสอง",
                "สมาร์ทปลั๊ก 2",
                "ปลั๊กสอง",
                "ปลั๊ก 2",
                "second",
                "number two",
            ),
            3: (
                "ตัวที่สาม",
                "ตัวที่ สาม",
                "ตัวที่ 3",
                "ตัว 3",
                "ตัวสาม",
                "อันที่สาม",
                "อันที่ 3",
                "อัน 3",
                "อันสาม",
                "เบอร์สาม",
                "เบอร์ 3",
                "หมายเลขสาม",
                "หมายเลข 3",
                "เครื่องที่สาม",
                "เครื่องที่ 3",
                "สมาร์ทปลั๊กสาม",
                "สมาร์ทปลั๊ก 3",
                "ปลั๊กสาม",
                "ปลั๊ก 3",
                "third",
                "number three",
            ),
        }

        for number, phrases in aliases.items():
            if any(
                phrase in text
                for phrase in phrases
            ):
                return number

        return None

    @classmethod
    def _find_development_alias_matches(
        cls,
        text: str,
        devices: list[SmartDevice],
    ) -> list[SmartDevice]:
        device_aliases: dict[
            str,
            tuple[str, ...],
        ] = {
            "light001": (
                "ไฟห้องนั่งเล่น",
                "หลอดไฟห้องนั่งเล่น",
                "living room light",
                "light living room",
            ),
            "light002": (
                "ไฟห้องนอน",
                "หลอดไฟห้องนอน",
                "bedroom light",
                "light bedroom",
            ),
            "fan001": (
                "พัดลมห้องนั่งเล่น",
                "พัดลม",
                "living room fan",
                "fan",
            ),
            "ac001": (
                "แอร์ห้องนอน",
                "เครื่องปรับอากาศห้องนอน",
                "แอร์",
                "bedroom air conditioner",
                "air conditioner",
                "ac",
            ),
            "garage001": (
                "ประตูโรงรถ",
                "ประตูการาจ",
                "โรงรถ",
                "garage door",
                "garage",
            ),
        }

        matches: list[SmartDevice] = []

        for device in devices:
            aliases = device_aliases.get(
                device.id,
                (),
            )

            if cls._matches_aliases(
                text,
                aliases,
            ):
                matches.append(
                    device
                )

        return matches

    @classmethod
    def _find_metadata_alias_matches(
        cls,
        text: str,
        devices: list[SmartDevice],
    ) -> list[SmartDevice]:
        matches: list[SmartDevice] = []

        for device in devices:
            aliases = cls._metadata_aliases(
                device
            )

            if cls._matches_aliases(
                text,
                aliases,
            ):
                matches.append(
                    device
                )

        return matches

    @classmethod
    def _metadata_aliases(
        cls,
        device: SmartDevice,
    ) -> tuple[str, ...]:
        aliases: list[str] = []

        device_name = cls._normalize(
            device.name
        )

        device_type = cls._normalize(
            device.device_type
        )

        # Tuya category "cz" = socket / smart plug.
        if (
            device_type == "cz"
            or "smart plug" in device_name
            or "socket" in device_name
        ):
            aliases.extend(
                (
                    "สมาร์ทปลั๊ก",
                    "สมาร์ทปลัก",
                    "สมาร์ทพลั๊ก",
                    "สมาร์ทพลัก",
                    "ปลั๊กอัจฉริยะ",
                    "ปลักอัจฉริยะ",
                    "ปลั๊ก",
                    "ปลัก",
                    "ปลั๊กไฟ",
                    "ปลักไฟ",
                    "smart plug",
                    "smartplug",
                    "smart socket",
                    "plug",
                    "socket",
                    "plak",
                    "pluk",
                    "plag",
                )
            )

        return tuple(
            aliases
        )

    @classmethod
    def _matches_aliases(
        cls,
        text: str,
        aliases: tuple[str, ...],
    ) -> bool:
        normalized_aliases = {
            cls._normalize(alias)
            for alias in aliases
        }

        return any(
            alias
            and alias in text
            for alias in normalized_aliases
        )

    @staticmethod
    def _unique_devices(
        devices: list[SmartDevice],
    ) -> list[SmartDevice]:
        unique: dict[str, SmartDevice] = {}

        for device in devices:
            unique[device.id] = device

        return list(
            unique.values()
        )

    @staticmethod
    def _normalize(
        text: str,
    ) -> str:
        return SmartHomeTextNormalizer.normalize(
            text
        )