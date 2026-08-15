from __future__ import annotations

import time
from typing import Any

from jarvis.agent.conversation_bridge import AIAgentConversationBridge
from jarvis.conversation.diagnostics import (
    ConversationDiagnosticsBuilder,
    ConversationDiagnosticsSnapshot,
)
from jarvis.conversation.execution_boundary import (
    ConversationExecutionBoundary,
    ConversationExecutionPolicy,
)
from jarvis.conversation.health_report import (
    ConversationHealthReport,
    ConversationHealthReporter,
)
from jarvis.conversation.operational_metrics import (
    ConversationOperationalMetrics,
    ConversationOperationalSnapshot,
)
from jarvis.conversation.recovery import ConversationRecoveryService
from jarvis.conversation.recovery_execution import (
    ConversationRecoveryExecutionResult,
    ConversationRecoveryExecutor,
)
from jarvis.conversation.turn import (
    ConversationTurnLifecycle,
    ConversationTurnResult,
    ConversationTurnSource,
)
from jarvis.core.event_bus import event_bus
from jarvis.core.events import Event
from jarvis.planner.conversation_bridge import PlannerConversationBridge
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
from jarvis.tools.conversation_bridge import (
    ToolCallingConversationBridge,
)


class ConversationManager:
    def __init__(
        self,
        ai: AIService,
        memory: MemoryService,
        router: ToolRouter,
        smart_home: SmartHomeService | None = None,
        capability_router: CapabilityRouter | None = None,
        capability_resolver: AICapabilityResolver | None = None,
        conversation_timeout_seconds: float = 60.0,
        recovery_service: ConversationRecoveryService | None = None,
        recovery_executor: ConversationRecoveryExecutor | None = None,
    ) -> None:
        self._ai = ai
        self._memory = memory
        self._router = router
        self._smart_home = smart_home
        self._capability_router = capability_router
        self._capability_resolver = capability_resolver
        self._planner_bridge: PlannerConversationBridge | None = None
        self._ai_agent_bridge: AIAgentConversationBridge | None = None
        self._tool_calling_bridge: ToolCallingConversationBridge | None = None
        self._turn_lifecycle = ConversationTurnLifecycle()
        self._diagnostics_builder = ConversationDiagnosticsBuilder()
        self._health_reporter = ConversationHealthReporter()
        self._operational_metrics = ConversationOperationalMetrics()
        self._execution_boundary = ConversationExecutionBoundary(
            ConversationExecutionPolicy(
                timeout_seconds=conversation_timeout_seconds
            )
        )
        self._recovery_service = (
            recovery_service
            if recovery_service is not None
            else ConversationRecoveryService()
        )
        self._recovery_executor = (
            recovery_executor
            if recovery_executor is not None
            else ConversationRecoveryExecutor()
        )

        self._device_resolver = (
            DeviceResolver(smart_home)
            if smart_home is not None
            else None
        )

        self._pending_smart_home = (
            PendingSmartHomeActionStore()
        )

    def set_ai_agent_bridge(
        self,
        bridge: AIAgentConversationBridge,
    ) -> None:
        self._ai_agent_bridge = bridge

    def set_planner_bridge(
        self,
        planner_bridge: PlannerConversationBridge,
    ) -> None:
        self._planner_bridge = planner_bridge

    def set_tool_calling_bridge(
        self,
        tool_calling_bridge: ToolCallingConversationBridge,
    ) -> None:
        self._tool_calling_bridge = tool_calling_bridge

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

    @property
    def last_turn(self) -> ConversationTurnResult | None:
        return self._turn_lifecycle.last_result

    @property
    def diagnostics_snapshot(
        self,
    ) -> ConversationDiagnosticsSnapshot | None:
        last_turn = self._turn_lifecycle.last_result

        if last_turn is None:
            return None

        return self._diagnostics_builder.build(
            last_turn
        )

    @property
    def operational_snapshot(
        self,
    ) -> ConversationOperationalSnapshot:
        return self._operational_metrics.snapshot()

    @property
    def health_report(
        self,
    ) -> ConversationHealthReport:
        return self._health_reporter.build(
            operational=self.operational_snapshot,
            latest_turn=self.diagnostics_snapshot,
        )

    @property
    def conversation_timeout_seconds(self) -> float:
        return self._execution_boundary.policy.timeout_seconds

    @property
    def max_recovery_attempts(self) -> int:
        return self._recovery_service.policy.max_recovery_attempts

    @property
    def recovery_safe_message(self) -> str:
        return self._recovery_executor.safe_message

    @property
    def last_recovery_execution(
        self,
    ) -> ConversationRecoveryExecutionResult | None:
        last_turn = self._turn_lifecycle.last_result

        if last_turn is None:
            return None

        execution = last_turn.recovery_execution

        if isinstance(
            execution,
            ConversationRecoveryExecutionResult,
        ):
            return execution

        return None

    def recovery_plan_for_last_turn(
        self,
        *,
        attempts: int = 0,
    ):
        last_turn = self._turn_lifecycle.last_result

        if (
            last_turn is None
            or last_turn.reliability is None
            or last_turn.reliability.failure is None
        ):
            return None

        return self._recovery_service.plan(
            failure=last_turn.reliability.failure,
            attempts=attempts,
        )

    def cancel_pending_smart_home(self) -> bool:
        if not self._pending_smart_home.has_pending:
            return False

        self._pending_smart_home.clear()

        return True

    async def ask(
        self,
        text: str,
        *,
        voice_mode: bool = False,
    ) -> str:
        normalized_text = text.strip()

        if not normalized_text:
            self._turn_lifecycle.empty(
                normalized_text
            )
            return ""

        source = self._predict_turn_source()

        async def run_legacy() -> str:
            if voice_mode:
                return await self._ask_legacy(
                    normalized_text,
                    voice_mode=True,
                )

            return await self._ask_legacy(
                normalized_text
            )

        try:
            result = await self._turn_lifecycle.run(
                user_text=normalized_text,
                source=source,
                handler=lambda: self._execution_boundary.run(
                    run_legacy
                ),
            )
        except Exception:
            recovery_plan = self.recovery_plan_for_last_turn(
                attempts=0
            )

            if recovery_plan is None:
                self._observe_latest_diagnostics()
                raise

            recovery_result = await self._recovery_executor.execute(
                outcome=recovery_plan,
                attempts_used=1,
                standard_ai_fallback=lambda: self._ai.ask(
                    text=normalized_text,
                    history=[],
                ),
            )

            if not recovery_result.executed:
                self._observe_latest_diagnostics()
                raise

            self._turn_lifecycle.mark_recovery_execution(
                recovery_result
            )
            self._observe_latest_diagnostics()

            return recovery_result.reply

        self._observe_latest_diagnostics()

        return result.reply

    def _observe_latest_diagnostics(
        self,
    ) -> None:
        snapshot = self.diagnostics_snapshot

        if snapshot is not None:
            self._operational_metrics.observe(
                snapshot
            )

    def _predict_turn_source(
        self,
    ) -> ConversationTurnSource:
        if (
            self._ai_agent_bridge is not None
            and self._ai_agent_bridge.has_pending_plan
        ):
            return ConversationTurnSource.AI_AGENT

        if (
            self._planner_bridge is not None
            and self._planner_bridge.has_pending_plan
        ):
            return ConversationTurnSource.PLANNER

        if self._pending_smart_home.has_pending:
            return ConversationTurnSource.SMART_HOME

        return ConversationTurnSource.UNKNOWN

    async def _ask_legacy(
        self,
        text: str,
        *,
        voice_mode: bool = False,
    ) -> str:
        text = text.strip()

        if not text:
            return ""

        if (
            self._ai_agent_bridge is not None
            and self._ai_agent_bridge.has_pending_plan
        ):
            agent_reply = (
                await self._ai_agent_bridge.handle_pending(
                    text
                )
            )

            if agent_reply.handled:
                self._turn_lifecycle.mark_source(
                    ConversationTurnSource.AI_AGENT
                )
                await self._save_conversation(
                    user_text=text,
                    reply=agent_reply.reply,
                    tool="ai_agent",
                )
                return agent_reply.reply

        if (
            self._planner_bridge is not None
            and self._planner_bridge.has_pending_plan
        ):
            planner_reply = await self._planner_bridge.handle_pending(
                text
            )
            if planner_reply.handled:
                self._turn_lifecycle.mark_source(
                    ConversationTurnSource.PLANNER
                )
                await self._save_conversation(
                    user_text=text,
                    reply=planner_reply.reply,
                    tool="planner",
                )
                return planner_reply.reply

        if self._pending_smart_home.has_pending:
            self._turn_lifecycle.mark_source(
                ConversationTurnSource.SMART_HOME
            )
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
                text,
                voice_mode=voice_mode,
            )

        elif tool_type == ToolType.SMART_HOME:
            self._turn_lifecycle.mark_source(
                ConversationTurnSource.SMART_HOME
            )
            reply = await self._handle_smart_home(
                text
            )

        elif tool_type == ToolType.SYSTEM:
            self._turn_lifecycle.mark_source(
                ConversationTurnSource.SYSTEM
            )
            reply = await self._handle_system(
                text
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
        *,
        voice_mode: bool = False,
    ) -> str:
        route_started = time.perf_counter()

        system_capability = self._resolve_system_capability(
            text
        )

        if (
            system_capability is not None
            and self._capability_router is not None
        ):
            started = time.perf_counter()

            result = await self._capability_router.execute(
                system_capability,
            )

            self._turn_lifecycle.mark_source(
                ConversationTurnSource.CAPABILITY
            )

            elapsed = time.perf_counter() - started

            print(
                "[Latency] Deterministic system : "
                f"{elapsed:.3f} s "
                f"({system_capability})"
            )

            return self._format_system_result(
                system_capability,
                result,
                user_text=text,
            )

        # Production fast path:
        # Native tool-calling AI can decide whether a tool is needed
        # in a single model turn.
        if self._tool_calling_bridge is not None:
            started = time.perf_counter()

            reply = await self._ask_ai(
                text,
                voice_mode=voice_mode,
            )

            elapsed = time.perf_counter() - started

            print(
                "[Latency] Fast native AI        : "
                f"{elapsed:.3f} s"
            )

            total = time.perf_counter() - route_started

            print(
                "[Latency] Fast AI route total   : "
                f"{total:.3f} s"
            )

            return reply

        # Compatibility path:
        # Used when native tool calling is unavailable.
        if (
            self._capability_resolver is not None
            and self._capability_router is not None
        ):
            started = time.perf_counter()

            request = await self._capability_resolver.resolve(
                text
            )

            elapsed = time.perf_counter() - started

            print(
                "[Latency] Capability fallback   : "
                f"{elapsed:.3f} s "
                f"(matched={request is not None})"
            )

            if request is not None:
                self._turn_lifecycle.mark_source(
                    ConversationTurnSource.CAPABILITY
                )

                result = (
                    await self._capability_router.execute_request(
                        request
                    )
                )

                total = (
                    time.perf_counter()
                    - route_started
                )

                print(
                    "[Latency] AI route total       : "
                    f"{total:.3f} s"
                )

                return self._format_capability_result(
                    request.capability,
                    result,
                )

        started = time.perf_counter()

        reply = await self._ask_ai(
            text,
            voice_mode=voice_mode,
        )

        elapsed = time.perf_counter() - started

        print(
            "[Latency] Standard AI fallback   : "
            f"{elapsed:.3f} s"
        )

        total = time.perf_counter() - route_started

        print(
            "[Latency] AI route total         : "
            f"{total:.3f} s"
        )

        return reply

    @staticmethod
    def _guard_voice_reply(
        *,
        user_text: str,
        reply: str,
    ) -> str:
        """Keep simple spoken recommendations concise.

        This guard is intentionally conservative. It only shortens
        recommendation-style replies when the user did not explicitly
        request details or an explanation.
        """
        normalized_user = user_text.strip().lower()
        normalized_reply = reply.strip()

        if not normalized_reply:
            return normalized_reply

        detail_markers = (
            "ทำไม",
            "เพราะอะไร",
            "อธิบาย",
            "รายละเอียด",
            "มีอะไรบ้าง",
            "กี่อย่าง",
            "หลาย",
            "ตัวเลือก",
            "ขั้นตอน",
            "วิธี",
            "why",
            "explain",
            "detail",
            "details",
            "options",
            "steps",
            "how",
        )

        if any(
            marker in normalized_user
            for marker in detail_markers
        ):
            return normalized_reply

        recommendation_markers = (
            "กินอะไรดี",
            "แนะนำอะไร",
            "เลือกอะไรดี",
            "เอาอะไรดี",
            "what should i eat",
            "what do you recommend",
            "what should i choose",
        )

        if not any(
            marker in normalized_user
            for marker in recommendation_markers
        ):
            return normalized_reply

        polite_endings = (
            "ครับ",
            "ค่ะ",
            "คะ",
        )

        for ending in polite_endings:
            search_from = 0

            while True:
                ending_index = normalized_reply.find(
                    ending,
                    search_from,
                )

                if ending_index == -1:
                    break

                candidate = normalized_reply[
                    : ending_index + len(ending)
                ].strip()

                if len(candidate) >= 8:
                    return candidate

                search_from = (
                    ending_index
                    + len(ending)
                )

        return normalized_reply

    async def _ask_ai(
        self,
        text: str,
        *,
        voice_mode: bool = False,
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

        if self._tool_calling_bridge is not None:
            if voice_mode:
                reply = await self._tool_calling_bridge.ask(
                    text=text,
                    history=history,
                    voice_mode=True,
                )
            else:
                reply = await self._tool_calling_bridge.ask(
                    text=text,
                    history=history,
                )

            self._turn_lifecycle.mark_source(
                ConversationTurnSource.FALLBACK_AI
                if self._tool_calling_bridge.last_used_fallback
                else ConversationTurnSource.NATIVE_TOOL
            )

        else:
            self._turn_lifecycle.mark_source(
                ConversationTurnSource.FALLBACK_AI
            )

            if voice_mode:
                reply = await self._ai.ask(
                    text=text,
                    history=history,
                    voice_mode=True,
                )
            else:
                reply = await self._ai.ask(
                    text=text,
                    history=history,
                )

        if voice_mode:
            reply = self._guard_voice_reply(
                user_text=text,
                reply=reply,
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


        datetime_phrases = (
            # Thai
            "วันนี้วันอะไร",
            "วันนี้วันที่เท่าไหร่",
            "วันนี้วันที่อะไร",
            "วันนี้วันไหน",
            "ตอนนี้กี่โมง",
            "ตอนนี้เวลาอะไร",
            "เวลาเท่าไหร่",

            # English
            "what time is it",
            "what day is it",
            "what is the date",
            "what's the date",
            "what is today's date",
            "what's today's date",
            "what's the date today",
        )

        ping_exact = (
            "ping",
            "system ping",
            "ทดสอบระบบ",
            "ระบบทำงานไหม",
            "ระบบทำงานหรือไม่",
        )

        health_exact = (
            "health",
            "health check",
            "system health",
            "system health check",
            "ตรวจสุขภาพระบบ",
            "ตรวจสอบระบบ",
            "สถานะระบบตอนนี้เป็นอย่างไร",
        )

        health_phrases = (
            "สถานะระบบ",
            "สุขภาพระบบ",
            "ระบบทำงานปกติ",
            "jarvis ทำงานปกติ",
            "jarvis ทำงานโอเค",
        )

        version_exact = (
            "version",
            "system version",
            "jarvis version",
            "jarvisai version",
            "เวอร์ชัน",
            "เวอร์ชั่น",
        )

        if normalized_text in ping_exact:
            return "system.ping"

        if normalized_text in health_exact:
            return "system.health"

        if any(
            phrase in normalized_text
            for phrase in health_phrases
        ):
            return "system.health"

        if normalized_text in version_exact:
            return "system.version"

        if any(
            phrase in normalized_text
            for phrase in datetime_phrases
        ):
            return "system.datetime"

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
        *,
        user_text: str | None = None,
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

        
        if capability == "system.datetime":
            if isinstance(result, dict):
                date_value = result.get("date")
                time_value = result.get("time")
                weekday = result.get("weekday")

                if (
                    isinstance(date_value, str)
                    and isinstance(time_value, str)
                    and isinstance(weekday, str)
                ):
                    try:
                        year_text, month_text, day_text = (
                            date_value.split("-")
                        )

                        year = int(year_text)
                        month = int(month_text)
                        day = int(day_text)

                        month_names = {
                            1: "มกราคม",
                            2: "กุมภาพันธ์",
                            3: "มีนาคม",
                            4: "เมษายน",
                            5: "พฤษภาคม",
                            6: "มิถุนายน",
                            7: "กรกฎาคม",
                            8: "สิงหาคม",
                            9: "กันยายน",
                            10: "ตุลาคม",
                            11: "พฤศจิกายน",
                            12: "ธันวาคม",
                        }

                        weekday_names = {
                            "Monday": "วันจันทร์",
                            "Tuesday": "วันอังคาร",
                            "Wednesday": "วันพุธ",
                            "Thursday": "วันพฤหัสบดี",
                            "Friday": "วันศุกร์",
                            "Saturday": "วันเสาร์",
                            "Sunday": "วันอาทิตย์",
                        }

                        month_th = month_names.get(
                            month,
                            month_text,
                        )

                        weekday_th = weekday_names.get(
                            weekday,
                            weekday,
                        )

                        short_time = time_value[:5]

                        normalized_text = (
                            user_text.lower().strip()
                            if user_text is not None
                            else ""
                        )

                        time_queries = (
                            "ตอนนี้กี่โมง",
                            "ตอนนี้เวลาอะไร",
                            "เวลาเท่าไหร่",
                            "what time is it",
                        )

                        date_queries = (
                            "วันนี้วันที่เท่าไหร่",
                            "วันนี้วันที่อะไร",
                            "what is the date",
                            "what's the date",
                            "what is today's date",
                            "what's today's date",
                            "what's the date today",
                        )

                        day_queries = (
                            "วันนี้วันอะไร",
                            "วันนี้วันไหน",
                            "what day is it",
                        )

                        if any(
                            phrase in normalized_text
                            for phrase in time_queries
                        ):
                            return (
                                "ครับ TK, ตอนนี้เวลา "
                                f"{short_time} น. ครับ"
                            )

                        if any(
                            phrase in normalized_text
                            for phrase in date_queries
                        ):
                            return (
                                "ครับ TK, วันนี้วันที่ "
                                f"{day} {month_th} "
                                f"{year} ครับ"
                            )

                        if any(
                            phrase in normalized_text
                            for phrase in day_queries
                        ):
                            return (
                                "ครับ TK, วันนี้"
                                f"{weekday_th}ครับ"
                            )

                        return (
                            "ครับ TK, ตอนนี้เวลา "
                            f"{short_time} น. "
                            f"{weekday_th}ที่ {day} "
                            f"{month_th} {year} ครับ"
                        )

                    except (
                        TypeError,
                        ValueError,
                    ):
                        return str(result)

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



        # ----------------------------    @classmethod
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

        # -----------------------------------------------------
        # Phase 0: explicit device number / ordinal
        # -----------------------------------------------------
        requested_number = (
            DeviceResolver._extract_requested_number(
                normalized_text
            )
        )

        if requested_number is not None:
            numbered_matches = [
                device
                for device in candidates
                if DeviceResolver._device_matches_number(
                    device,
                    requested_number,
                )
            ]

            numbered_matches = cls._unique_devices(
                numbered_matches
            )

            if numbered_matches:
                return numbered_matches

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
            "สถานะอุปกรณ์ smart home",
            "สถานะอุปกรณ์ทั้งหมด",
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