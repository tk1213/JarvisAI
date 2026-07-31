from __future__ import annotations

from enum import Enum


class ToolType(str, Enum):
    AI = "ai"
    SMART_HOME = "smart_home"
    SYSTEM = "system"
    PLUGIN = "plugin"


class ToolRouter:
    def route(
        self,
        text: str,
    ) -> ToolType:
        """
        Determine which subsystem should handle the request.
        """

        text = text.lower().strip()

        smart_home_keywords = [
            "เปิดไฟ",
            "ปิดไฟ",
            "ไฟ",
            "หลอดไฟ",
            "พัดลม",
            "แอร์",
            "ปลั๊ก",
        ]

        system_keywords = [
            "ปิดโปรแกรม",
            "shutdown",
            "restart",
            "รีสตาร์ท",
        ]

        plugin_keywords = [
            "เล่นเพลง",
            "เปิดเพลง",
            "music",
        ]

        if any(keyword in text for keyword in smart_home_keywords):
            return ToolType.SMART_HOME

        if any(keyword in text for keyword in system_keywords):
            return ToolType.SYSTEM

        if any(keyword in text for keyword in plugin_keywords):
            return ToolType.PLUGIN

        return ToolType.AI