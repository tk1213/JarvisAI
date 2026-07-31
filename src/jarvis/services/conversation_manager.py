from __future__ import annotations

from jarvis.core.event_bus import event_bus
from jarvis.core.events import Event
from jarvis.services.ai_service import AIService
from jarvis.services.memory_service import MemoryService
from jarvis.services.tool_router import ToolRouter, ToolType
from jarvis.smart_home.device import SmartDevice
from jarvis.smart_home.service import SmartHomeService


class ConversationManager:
    def __init__(
        self,
        ai: AIService,
        memory: MemoryService,
        router: ToolRouter,
        smart_home: SmartHomeService | None = None,
    ) -> None:
        self._ai = ai
        self._memory = memory
        self._router = router
        self._smart_home = smart_home

    async def ask(
        self,
        text: str,
    ) -> str:
        text = text.strip()

        if not text:
            return ""

        tool_type = self._router.route(text)

        await event_bus.publish(
            Event(
                name="conversation.request",
                payload={
                    "text": text,
                    "tool": tool_type.value,
                },
            )
        )

        if tool_type == ToolType.AI:
            reply = await self._ask_ai(text)

        elif tool_type == ToolType.SMART_HOME:
            reply = await self._handle_smart_home(text)

        elif tool_type == ToolType.SYSTEM:
            reply = "ระบบคำสั่งควบคุมเครื่องยังไม่ได้เชื่อมต่อครับ"

        elif tool_type == ToolType.PLUGIN:
            reply = "ระบบ Plugin ยังไม่ได้เชื่อมต่อครับ"

        else:
            reply = "ไม่สามารถเลือกเครื่องมือสำหรับคำสั่งนี้ได้ครับ"

        await self._memory.save_message(
            role="user",
            content=text,
        )

        await self._memory.save_message(
            role="assistant",
            content=reply,
        )

        await event_bus.publish(
            Event(
                name="conversation.response",
                payload={
                    "text": reply,
                    "tool": tool_type.value,
                },
            )
        )

        return reply

    async def _ask_ai(
        self,
        text: str,
    ) -> str:
        await event_bus.publish(
            Event(
                name="ai.request",
                payload={
                    "text": text,
                },
            )
        )

        history = await self._memory.get_ai_history()

        reply = await self._ai.ask(
            text=text,
            history=history,
        )

        await event_bus.publish(
            Event(
                name="ai.response",
                payload={
                    "text": reply,
                },
            )
        )

        return reply

    async def _handle_smart_home(
        self,
        text: str,
    ) -> str:
        if self._smart_home is None:
            return "ระบบ Smart Home ยังไม่ได้เชื่อมต่อครับ"

        normalized_text = text.lower().strip()

        if self._is_list_command(normalized_text):
            return await self._list_smart_home_devices()

        device = await self._find_device(normalized_text)

        if device is None:
            return "ไม่พบอุปกรณ์ Smart Home ที่ตรงกับคำสั่งครับ"

        if self._is_turn_off_command(normalized_text):
            success = await self._smart_home.turn_off(device.id)

            if success:
                return f"ปิด {device.name} แล้วครับ"

            return f"ไม่สามารถปิด {device.name} ได้ครับ"

        if self._is_turn_on_command(normalized_text):
            success = await self._smart_home.turn_on(device.id)

            if success:
                return f"เปิด {device.name} แล้วครับ"

            return f"ไม่สามารถเปิด {device.name} ได้ครับ"

        if self._is_toggle_command(normalized_text):
            success = await self._smart_home.toggle(device.id)

            if not success:
                return f"ไม่สามารถสลับสถานะ {device.name} ได้ครับ"

            updated_device = await self._smart_home.get_device(device.id)

            if updated_device is None:
                return f"สลับสถานะ {device.name} แล้วครับ"

            state = "เปิด" if updated_device.power else "ปิด"
            return f"{device.name} อยู่ในสถานะ{state}แล้วครับ"

        if self._is_status_command(normalized_text):
            state = "เปิด" if device.power else "ปิด"
            online = "ออนไลน์" if device.online else "ออฟไลน์"

            return (
                f"{device.name} อยู่ในสถานะ{state} "
                f"และอุปกรณ์{online}ครับ"
            )

        return (
            f"พบอุปกรณ์ {device.name} แต่ยังไม่ทราบว่าต้องการ"
            "เปิด ปิด สลับสถานะ หรือตรวจสอบสถานะครับ"
        )

    async def _find_device(
        self,
        text: str,
    ) -> SmartDevice | None:
        if self._smart_home is None:
            return None

        devices = await self._smart_home.list_devices()

        device_aliases: dict[str, tuple[str, ...]] = {
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

        for device in devices:
            aliases = device_aliases.get(device.id, ())

            if any(alias in text for alias in aliases):
                return device

            if device.name.lower() in text:
                return device

        return None

    async def _list_smart_home_devices(self) -> str:
        if self._smart_home is None:
            return "ระบบ Smart Home ยังไม่ได้เชื่อมต่อครับ"

        devices = await self._smart_home.list_devices()

        if not devices:
            return "ยังไม่มีอุปกรณ์ Smart Home ในระบบครับ"

        device_descriptions = []

        for device in devices:
            power_state = "เปิด" if device.power else "ปิด"
            online_state = "ออนไลน์" if device.online else "ออฟไลน์"

            device_descriptions.append(
                f"{device.name}: {power_state}, {online_state}"
            )

        return "อุปกรณ์ Smart Home ที่พบ: " + "; ".join(
            device_descriptions
        )

    @staticmethod
    def _is_turn_on_command(text: str) -> bool:
        keywords = (
            "เปิด",
            "turn on",
            "switch on",
        )
        return any(keyword in text for keyword in keywords)

    @staticmethod
    def _is_turn_off_command(text: str) -> bool:
        keywords = (
            "ปิด",
            "turn off",
            "switch off",
        )
        return any(keyword in text for keyword in keywords)

    @staticmethod
    def _is_toggle_command(text: str) -> bool:
        keywords = (
            "สลับ",
            "toggle",
        )
        return any(keyword in text for keyword in keywords)

    @staticmethod
    def _is_status_command(text: str) -> bool:
        keywords = (
            "สถานะ",
            "เป็นอย่างไร",
            "status",
            "state",
        )
        return any(keyword in text for keyword in keywords)

    @staticmethod
    def _is_list_command(text: str) -> bool:
        keywords = (
            "รายการอุปกรณ์",
            "อุปกรณ์ทั้งหมด",
            "มีอุปกรณ์อะไร",
            "list devices",
            "all devices",
        )
        return any(keyword in text for keyword in keywords)