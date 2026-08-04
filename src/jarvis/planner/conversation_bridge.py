from __future__ import annotations

from dataclasses import dataclass

from jarvis.planner.orchestrator import PlannerOrchestrator


@dataclass(slots=True)
class PlannerConversationReply:
    handled: bool
    reply: str = ""


class PlannerConversationBridge:
    _CONFIRM_WORDS = frozenset(
        {
            "confirm",
            "yes",
            "ok",
            "okay",
            "ยืนยัน",
            "ตกลง",
        }
    )
    _CANCEL_WORDS = frozenset(
        {
            "cancel",
            "no",
            "never mind",
            "nevermind",
            "ยกเลิก",
            "ไม่",
        }
    )

    def __init__(
        self,
        orchestrator: PlannerOrchestrator,
    ) -> None:
        self._orchestrator = orchestrator

    @property
    def has_pending_plan(self) -> bool:
        return self._orchestrator.has_pending_plan

    async def handle_pending(
        self,
        text: str,
    ) -> PlannerConversationReply:
        if not self.has_pending_plan:
            return PlannerConversationReply(False)

        normalized = text.strip().casefold()

        if normalized in self._CONFIRM_WORDS:
            result = await self._orchestrator.confirm_pending()
            return PlannerConversationReply(
                True,
                self._format_execution(result),
            )

        if normalized in self._CANCEL_WORDS:
            self._orchestrator.cancel_pending()
            return PlannerConversationReply(
                True,
                "ยกเลิกแผนแล้วครับ",
            )

        return PlannerConversationReply(
            True,
            "มีแผนที่รอการยืนยันอยู่ครับ "
            "พิมพ์ 'ยืนยัน' เพื่อดำเนินการ หรือ 'ยกเลิก' เพื่อยกเลิก",
        )

    async def handle_ai_request(
        self,
        text: str,
    ) -> PlannerConversationReply:
        preview = await self._orchestrator.prepare(text)

        if preview is None:
            return PlannerConversationReply(False)

        if preview.requires_confirmation:
            steps = "; ".join(
                f"{step.capability} {step.arguments}"
                for step in preview.plan.steps
            )
            return PlannerConversationReply(
                True,
                "แผนนี้มีการเปลี่ยนแปลงอุปกรณ์และต้องยืนยันก่อนครับ: "
                f"{steps}. พิมพ์ 'ยืนยัน' หรือ 'ยกเลิก'",
            )

        result = await self._orchestrator.execute_preview(preview)
        return PlannerConversationReply(
            True,
            self._format_execution(result),
        )

    @staticmethod
    def _format_execution(result) -> str:
        if result.success:
            return "ดำเนินการตามแผนสำเร็จครับ"

        failed = [
            item
            for item in result.step_results
            if not item.success
        ]
        if failed:
            return (
                "ดำเนินการตามแผนไม่สำเร็จที่ขั้นตอน "
                f"{failed[0].capability} ครับ"
            )

        return "ดำเนินการตามแผนไม่สำเร็จครับ"
