from __future__ import annotations

from typing import Any

from jarvis.core.event_bus import event_bus
from jarvis.core.events import Event
from jarvis.services.ai_capability_resolver import AICapabilityResolver
from jarvis.services.ai_service import AIService
from jarvis.services.capability_router import CapabilityRouter
from jarvis.services.memory_service import MemoryService
from jarvis.services.tool_router import ToolRouter, ToolType
from jarvis.smart_home.device import SmartDevice
from jarvis.smart_home.pending_action import (
    PendingSmartHomeAction,
    PendingSmartHomeActionStore,
    SmartHomeAction,
)
from jarvis.smart_home.resolution import DeviceResolutionStatus
from jarvis.smart_home.resolver import DeviceResolver
from jarvis.smart_home.service import SmartHomeService


class ConversationManager:
    def __init__(
        self,
        ai: AIService,
        memory: MemoryService,
        router: ToolRouter,
        smart_home: SmartHomeService | None = None,
        capability_router: CapabilityRouter | None = None,
        capability_resolver: AICapabilityResolver | None = None,
    ) -> None:
        self._ai = ai
        self._memory = memory
        self._router = router
        self._smart_home = smart_home
        self._capability_router = capability_router
        self._capability_resolver = capability_resolver

        self._device_resolver = (
            DeviceResolver(smart_home)
            if smart_home is not None
            else None
        )

        self._pending_smart_home = (
            PendingSmartHomeActionStore()
        )

    def set_capability_router(
        self,
        capability_router: CapabilityRouter,
    ) -> None:
        self._capability_router = capability_router

    def set_capability_resolver(
        self,
        capability_resolver: AICapabilityResolver,
    ) -> None:
        self._capability_resolver = capability_resolver

    @property
    def has_pending_smart_home(self) -> bool:
        return self._pending_smart_home.has_pending    

    async def ask(
        self,
        text: str,
    ) -> str:
        text = text.strip()

        if not text:
            return ""

        if self._pending_smart_home.has_pending:
            reply = await self._handle_pending_smart_home(
                text
            )

            await self._save_conversation(
                user_text=text,
                reply=reply,
                tool="smart_home",
            )

            return reply

        tool_type = self._router.route(
            text
        )

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
            reply = await self._handle_ai_route(
                text
            )

        elif tool_type == ToolType.SMART_HOME:
            reply = await self._handle_smart_home(
                text
            )

        elif tool_type == ToolType.SYSTEM:
            reply = await self._handle_system(
                text
            )

        elif tool_type == ToolType.PLUGIN:
            reply = (
                "ระบบ Plugin "
                "ยังไม่ได้เชื่อมต่อครับ"
            )

        else:
            reply = (
                "ไม่สามารถเลือกเครื่องมือ"
                "สำหรับคำสั่งนี้ได้ครับ"
            )

        await self._save_conversation(
            user_text=text,
            reply=reply,
            tool=tool_type.value,
        )

        return reply

    async def _save_conversation(
        self,
        *,
        user_text: str,
        reply: str,
        tool: str,
    ) -> None:
        await self._memory.save_message(
            role="user",
            content=user_text,
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
                    "tool": tool,
                },
            )
        )

    async def _handle_ai_route(
        self,
        text: str,
    ) -> str:
        if (
            self._capability_resolver is not None
            and self._capability_router is not None
        ):
            request = (
                await self._capability_resolver.resolve(
                    text,
                )
            )

            if request is not None:
                result = (
                    await self._capability_router.execute_request(
                        request,
                    )
                )

                return self._format_capability_result(
                    request.capability,
                    result,
                )

        return await self._ask_ai(
            text
        )

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

    async def _handle_system(
        self,
        text: str,
    ) -> str:
        if self._capability_router is None:
            return (
                "ระบบคำสั่งควบคุมเครื่อง"
                "ยังไม่ได้เชื่อมต่อครับ"
            )

        capability = self._resolve_system_capability(
            text
        )

        if capability is None:
            return (
                "ไม่พบคำสั่งระบบ"
                "ที่ตรงกับคำสั่งนี้ครับ"
            )

        result = await self._capability_router.execute(
            capability,
        )

        return self._format_system_result(
            capability,
            result,
        )

    @staticmethod
    def _resolve_system_capability(
        text: str,
    ) -> str | None:
        normalized_text = text.lower().strip()

        ping_keywords = (
            "ping",
            "ทดสอบระบบ",
            "ระบบทำงานไหม",
            "ระบบทำงานหรือไม่",
        )

        health_keywords = (
            "health",
            "health check",
            "ตรวจสุขภาพระบบ",
            "ตรวจสอบระบบ",
        )

        version_keywords = (
            "version",
            "เวอร์ชัน",
            "เวอร์ชั่น",
        )

        if any(
            keyword in normalized_text
            for keyword in ping_keywords
        ):
            return "system.ping"

        if any(
            keyword in normalized_text
            for keyword in health_keywords
        ):
            return "system.health"

        if any(
            keyword in normalized_text
            for keyword in version_keywords
        ):
            return "system.version"

        return None

    @staticmethod
    def _format_capability_result(
        capability: str,
        result: Any,
    ) -> str:
        if capability.startswith(
            "system."
        ):
            return ConversationManager._format_system_result(
                capability,
                result,
            )

        return str(
            result
        )

    @staticmethod
    def _format_system_result(
        capability: str,
        result: Any,
    ) -> str:
        if capability == "system.ping":
            if (
                isinstance(result, dict)
                and result.get("status") == "ok"
            ):
                return (
                    "ระบบ JarvisAI "
                    "ทำงานปกติครับ"
                )

            return str(result)

        if capability == "system.health":
            if isinstance(
                result,
                dict,
            ):
                if result.get(
                    "healthy",
                    False,
                ):
                    return (
                        "ระบบ JarvisAI "
                        "อยู่ในสถานะปกติครับ"
                    )

                return (
                    "ระบบ JarvisAI "
                    "พบสถานะผิดปกติครับ"
                )

            return str(result)

        if capability == "system.version":
            if isinstance(
                result,
                dict,
            ):
                version = result.get(
                    "jarvis"
                )

                if version is not None:
                    return (
                        f"JarvisAI Version {version}"
                    )

            return str(result)

        return str(result)

    async def _handle_smart_home(
        self,
        text: str,
    ) -> str:
        if self._smart_home is None:
            return (
                "ระบบ Smart Home "
                "ยังไม่ได้เชื่อมต่อครับ"
            )

        normalized_text = (
            DeviceResolver._normalize(
                text
            )
        )

        if self._is_list_command(
            normalized_text
        ):
            return await self._list_smart_home_devices()

        if self._device_resolver is None:
            return (
                "ระบบค้นหาอุปกรณ์ Smart Home "
                "ยังไม่ได้เชื่อมต่อครับ"
            )

        action = self._resolve_smart_home_action(
            normalized_text
        )

        resolution = (
            await self._device_resolver.resolve_detailed(
                normalized_text
            )
        )

        if (
            resolution.status
            is DeviceResolutionStatus.NOT_FOUND
        ):
            return (
                "ไม่พบอุปกรณ์ Smart Home "
                "ที่ตรงกับคำสั่งครับ"
            )

        if (
            resolution.status
            is DeviceResolutionStatus.AMBIGUOUS
        ):
            if action is not None:
                self._pending_smart_home.set(
                    PendingSmartHomeAction(
                        action=action,
                        candidates=resolution.candidates,
                    )
                )

            return self._format_ambiguous_devices(
                resolution.candidates
            )

        device = resolution.device

        if device is None:
            return (
                "ไม่สามารถระบุอุปกรณ์ "
                "Smart Home ได้ครับ"
            )

        if action is None:
            return (
                f"พบอุปกรณ์ {device.name} "
                "แต่ยังไม่ทราบว่าต้องการ "
                "เปิด ปิด สลับสถานะ "
                "หรือตรวจสอบสถานะครับ"
            )

        return await self._execute_smart_home_action(
            action=action,
            device=device,
        )

    async def _handle_pending_smart_home(
        self,
        text: str,
    ) -> str:
        pending = self._pending_smart_home.pending

        if pending is None:
            return (
                "ไม่มีคำสั่ง Smart Home "
                "ที่กำลังรอการยืนยันครับ"
            )

        normalized_text = (
            DeviceResolver._normalize(
                text
            )
        )

        if self._is_cancel_command(
            normalized_text
        ):
            self._pending_smart_home.clear()

            return (
                "ยกเลิกคำสั่ง Smart Home "
                "แล้วครับ"
            )

        matches = self._match_pending_candidates(
            normalized_text,
            pending.candidates,
        )

        if len(matches) == 1:
            device = matches[0]
            action = pending.action

            self._pending_smart_home.clear()

            return await self._execute_smart_home_action(
                action=action,
                device=device,
            )

        if len(matches) > 1:
            return (
                "คำตอบยังตรงกับอุปกรณ์"
                "มากกว่า 1 ตัวครับ "
                + self._format_ambiguous_devices(
                    tuple(matches)
                )
            )

        return (
            "ยังไม่สามารถระบุอุปกรณ์"
            "จากคำตอบได้ครับ "
            + self._format_ambiguous_devices(
                pending.candidates
            )
        )

    @classmethod
    def _match_pending_candidates(
        cls,
        text: str,
        candidates: tuple[SmartDevice, ...],
    ) -> list[SmartDevice]:
        normalized_text = (
            DeviceResolver._normalize(
                text
            )
        )

        ordinal_index = cls._extract_device_ordinal(
            normalized_text
        )

        if ordinal_index is not None:
            if 0 <= ordinal_index < len(candidates):
                return [
                    candidates[ordinal_index]
                ]

            return []

        # -----------------------------------------------------
        # Phase 1: exact device ID / name / room
        # -----------------------------------------------------
        exact_matches: list[SmartDevice] = []

        for device in candidates:
            direct_aliases = {
                DeviceResolver._normalize(
                    device.id
                ),
                DeviceResolver._normalize(
                    device.name
                ),
            }

            room = DeviceResolver._normalize(
                device.room
            )

            if room:
                direct_aliases.add(
                    room
                )

            if normalized_text in direct_aliases:
                exact_matches.append(
                    device
                )

        exact_matches = cls._unique_devices(
            exact_matches
        )

        if exact_matches:
            return exact_matches

        # -----------------------------------------------------
        # Phase 2: exact candidate aliases
        # -----------------------------------------------------
        alias_matches: list[SmartDevice] = []

        for device in candidates:
            aliases = cls._candidate_aliases(
                device
            )

            if normalized_text in aliases:
                alias_matches.append(
                    device
                )

        alias_matches = cls._unique_devices(
            alias_matches
        )

        if alias_matches:
            return alias_matches

        # -----------------------------------------------------
        # Phase 3: longest partial alias
        # -----------------------------------------------------
        scored_matches: list[
            tuple[int, SmartDevice]
        ] = []

        for device in candidates:
            aliases = cls._candidate_aliases(
                device
            )

            matching_aliases = [
                alias
                for alias in aliases
                if alias
                and alias in normalized_text
            ]

            if not matching_aliases:
                continue

            best_alias_length = max(
                len(alias)
                for alias in matching_aliases
            )

            scored_matches.append(
                (
                    best_alias_length,
                    device,
                )
            )

        if not scored_matches:
            return []

        best_score = max(
            score
            for score, _device in scored_matches
        )

        best_devices = [
            device
            for score, device in scored_matches
            if score == best_score
        ]

        return cls._unique_devices(
            best_devices
        )

    @staticmethod
    def _candidate_aliases(
        device: SmartDevice,
    ) -> tuple[str, ...]:
        aliases: set[str] = {
            DeviceResolver._normalize(
                device.id
            ),
            DeviceResolver._normalize(
                device.name
            ),
        }

        room = DeviceResolver._normalize(
            device.room
        )

        if room:
            aliases.add(
                room
            )

        name = DeviceResolver._normalize(
            device.name
        )

        if "smart plug" in name:
            aliases.add(
                DeviceResolver._normalize(
                    name.replace(
                        "smart plug",
                        "สมาร์ทปลั๊ก",
                    )
                )
            )

            aliases.add(
                DeviceResolver._normalize(
                    name.replace(
                        "smart plug",
                        "ปลั๊ก",
                    )
                )
            )

        if (
            "bedroom" in name
            or "bed room" in name
            or "bedroom" in room
        ):
            aliases.update(
                {
                    DeviceResolver._normalize(
                        "ห้องนอน"
                    ),
                    DeviceResolver._normalize(
                        "ในห้องนอน"
                    ),
                    DeviceResolver._normalize(
                        "ตัวห้องนอน"
                    ),
                    "bedroom",
                    "bed room",
                }
            )

        if (
            "living room" in name
            or "livingroom" in name
            or "living room" in room
        ):
            aliases.update(
                {
                    DeviceResolver._normalize(
                        "ห้องนั่งเล่น"
                    ),
                    DeviceResolver._normalize(
                        "ในห้องนั่งเล่น"
                    ),
                    DeviceResolver._normalize(
                        "ตัวห้องนั่งเล่น"
                    ),
                    "living room",
                    "livingroom",
                }
            )

        if (
            "garage" in name
            or "garage" in room
        ):
            aliases.update(
                {
                    DeviceResolver._normalize(
                        "โรงรถ"
                    ),
                    DeviceResolver._normalize(
                        "ห้องโรงรถ"
                    ),
                    "garage",
                }
            )

        return tuple(
            alias
            for alias in aliases
            if alias
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

    async def _execute_smart_home_action(
        self,
        *,
        action: SmartHomeAction,
        device: SmartDevice,
    ) -> str:
        if self._smart_home is None:
            return (
                "ระบบ Smart Home "
                "ยังไม่ได้เชื่อมต่อครับ"
            )

        if action is SmartHomeAction.TURN_ON:
            success = await self._smart_home.turn_on(
                device.id,
            )

            if success:
                return (
                    f"เปิด {device.name} แล้วครับ"
                )

            return (
                f"ไม่สามารถเปิด "
                f"{device.name} ได้ครับ"
            )

        if action is SmartHomeAction.TURN_OFF:
            success = await self._smart_home.turn_off(
                device.id,
            )

            if success:
                return (
                    f"ปิด {device.name} แล้วครับ"
                )

            return (
                f"ไม่สามารถปิด "
                f"{device.name} ได้ครับ"
            )

        if action is SmartHomeAction.TOGGLE:
            success = await self._smart_home.toggle(
                device.id,
            )

            if not success:
                return (
                    "ไม่สามารถสลับสถานะ "
                    f"{device.name} ได้ครับ"
                )

            updated_device = (
                await self._smart_home.get_device(
                    device.id,
                )
            )

            if updated_device is None:
                return (
                    f"สลับสถานะ "
                    f"{device.name} แล้วครับ"
                )

            state = (
                "เปิด"
                if updated_device.power
                else "ปิด"
            )

            return (
                f"{device.name} "
                f"อยู่ในสถานะ{state}แล้วครับ"
            )

        if action is SmartHomeAction.STATUS:
            updated_device = (
                await self._smart_home.get_device(
                    device.id,
                )
            )

            current_device = (
                updated_device
                if updated_device is not None
                else device
            )

            state = (
                "เปิด"
                if current_device.power
                else "ปิด"
            )

            online = (
                "ออนไลน์"
                if current_device.online
                else "ออฟไลน์"
            )

            return (
                f"{current_device.name} "
                f"อยู่ในสถานะ{state} "
                f"และอุปกรณ์{online}ครับ"
            )

        return (
            "ไม่รองรับคำสั่ง Smart Home "
            "ประเภทนี้ครับ"
        )

    @classmethod
    def _resolve_smart_home_action(
        cls,
        text: str,
    ) -> SmartHomeAction | None:
        if cls._is_turn_on_command(
            text
        ):
            return SmartHomeAction.TURN_ON

        if cls._is_turn_off_command(
            text
        ):
            return SmartHomeAction.TURN_OFF

        if cls._is_toggle_command(
            text
        ):
            return SmartHomeAction.TOGGLE

        if cls._is_status_command(
            text
        ):
            return SmartHomeAction.STATUS

        return None

    @staticmethod
    def _format_ambiguous_devices(
        candidates: tuple[SmartDevice, ...],
    ) -> str:
        names = [
            candidate.name
            for candidate in candidates
        ]

        if not names:
            return (
                "พบอุปกรณ์ที่ตรงกัน"
                "มากกว่า 1 ตัวครับ "
                "กรุณาระบุอุปกรณ์"
                "ให้ชัดเจนขึ้นครับ"
            )

        device_list = " หรือ ".join(
            names
        )

        return (
            "พบอุปกรณ์ที่ตรงกัน"
            "มากกว่า 1 ตัวครับ "
            f"ต้องการ {device_list} ครับ?"
        )

    async def _list_smart_home_devices(
        self,
    ) -> str:
        if self._smart_home is None:
            return (
                "ระบบ Smart Home "
                "ยังไม่ได้เชื่อมต่อครับ"
            )

        devices = await self._smart_home.list_devices()

        if not devices:
            return (
                "ยังไม่มีอุปกรณ์ "
                "Smart Home ในระบบครับ"
            )

        device_descriptions: list[str] = []

        for device in devices:
            power_state = (
                "เปิด"
                if device.power
                else "ปิด"
            )

            online_state = (
                "ออนไลน์"
                if device.online
                else "ออฟไลน์"
            )

            device_descriptions.append(
                f"{device.name}: "
                f"{power_state}, "
                f"{online_state}"
            )

        return (
            "อุปกรณ์ Smart Home ที่พบ: "
            + "; ".join(
                device_descriptions
            )
        )

    @staticmethod
    def _is_turn_on_command(
        text: str,
    ) -> bool:
        keywords = (
            "เปิด",
            "turn on",
            "switch on",
        )

        return any(
            keyword in text
            for keyword in keywords
        )

    @staticmethod
    def _is_turn_off_command(
        text: str,
    ) -> bool:
        keywords = (
            "ปิด",
            "turn off",
            "switch off",
        )

        return any(
            keyword in text
            for keyword in keywords
        )

    @staticmethod
    def _is_toggle_command(
        text: str,
    ) -> bool:
        keywords = (
            "สลับ",
            "toggle",
        )

        return any(
            keyword in text
            for keyword in keywords
        )

    @staticmethod
    def _is_status_command(
        text: str,
    ) -> bool:
        keywords = (
            "สถานะ",
            "เป็นอย่างไร",
            "status",
            "state",
        )

        return any(
            keyword in text
            for keyword in keywords
        )

    @staticmethod
    def _is_list_command(
        text: str,
    ) -> bool:
        keywords = (
            "รายการอุปกรณ์",
            "อุปกรณ์ทั้งหมด",
            "มีอุปกรณ์อะไร",
            "list devices",
            "all devices",
        )

        return any(
            keyword in text
            for keyword in keywords
        )

    @staticmethod
    def _is_cancel_command(
        text: str,
    ) -> bool:
        keywords = (
            "ยกเลิก",
            "ไม่เอา",
            "ไม่ต้อง",
            "cancel",
            "never mind",
            "nevermind",
        )

        return any(
            keyword in text
            for keyword in keywords
        )