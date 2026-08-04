from __future__ import annotations

from enum import Enum

from jarvis.smart_home.text_normalizer import (
    SmartHomeTextNormalizer,
)


class ToolType(str, Enum):
    AI = "ai"
    SMART_HOME = "smart_home"
    SYSTEM = "system"
    PLUGIN = "plugin"


class ToolRouter:
    """
    Route user requests to the appropriate Jarvis subsystem.

    Routing priority:
    1. System
    2. Plugin
    3. Smart Home
    4. AI fallback

    Smart Home text normalization is handled by
    SmartHomeTextNormalizer.
    """

    def route(
        self,
        text: str,
    ) -> ToolType:
        normalized_text = (
            SmartHomeTextNormalizer.normalize(
                text
            )
        )

        if self._is_system_command(
            normalized_text
        ):
            return ToolType.SYSTEM

        if self._is_plugin_command(
            normalized_text
        ):
            return ToolType.PLUGIN

        if self._is_smart_home_command(
            normalized_text
        ):
            return ToolType.SMART_HOME

        return ToolType.AI

    @staticmethod
    def _is_smart_home_command(
        text: str,
    ) -> bool:
        smart_home_keywords = (
            # Thai actions
            "เปิด",
            "ปิด",
            "สลับ",
            "สถานะ",

            # Thai devices
            "ไฟ",
            "หลอดไฟ",
            "พัดลม",
            "แอร์",
            "เครื่องปรับอากาศ",
            "ประตูโรงรถ",
            "โรงรถ",
            "ปลั๊ก",
            "สมาร์ทปลั๊ก",

            # Thai device queries
            "อุปกรณ์ทั้งหมด",
            "รายการอุปกรณ์",
            "มีอุปกรณ์อะไร",

            # English devices
            "smart plug",
            "socket",
            "light",
            "fan",
            "air conditioner",
            "garage",

            # English actions
            "turn on",
            "turn off",
            "switch on",
            "switch off",
            "toggle",

            # English device queries
            "list devices",
            "all devices",
        )

        return any(
            keyword in text
            for keyword in smart_home_keywords
        )

    @staticmethod
    def _is_plugin_command(
        text: str,
    ) -> bool:
        plugin_keywords = (
            "เล่นเพลง",
            "เปิดเพลง",
            "ปิดเพลง",
            "หยุดเพลง",
            "เพลง",
            "music",
            "play music",
            "stop music",
        )

        return any(
            keyword in text
            for keyword in plugin_keywords
        )

    @staticmethod
    def _is_system_command(
        text: str,
    ) -> bool:
        exact_commands = (
            # English
            "shutdown",
            "restart",
            "system version",
            "jarvis version",
            "system health",
            "jarvis health",
            "system ping",
            "jarvis ping",

            # Thai
            "ปิดโปรแกรม",
            "รีสตาร์ท",
            "เวอร์ชันระบบ",
            "เวอร์ชั่นระบบ",
            "เวอร์ชัน jarvis",
            "เวอร์ชั่น jarvis",
            "ตรวจสุขภาพระบบ",
            "ตรวจสอบระบบ",
            "ตรวจสอบระบบ jarvis",
            "ทดสอบระบบ",
            "ระบบทำงานไหม",
            "ระบบทำงานหรือไม่",
        )

        return text in exact_commands