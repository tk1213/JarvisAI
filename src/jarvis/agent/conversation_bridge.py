from __future__ import annotations

from dataclasses import dataclass

from jarvis.agent.report import AIAgentRunReportBuilder
from jarvis.agent.runtime import (
    AIAgentRunStatus,
    AIAgentRuntime,
)


@dataclass(slots=True, frozen=True)
class AIAgentConversationReply:
    handled: bool
    reply: str


class AIAgentConversationBridge:
    def __init__(
        self,
        runtime: AIAgentRuntime,
    ) -> None:
        self._runtime = runtime
        self._report_builder = AIAgentRunReportBuilder()

    @property
    def has_pending_plan(self) -> bool:
        return self._runtime.has_pending_plan

    async def handle_ai_request(
        self,
        text: str,
    ) -> AIAgentConversationReply:
        result = await self._runtime.run(text)

        if result.status is AIAgentRunStatus.NO_PLAN:
            return AIAgentConversationReply(
                handled=False,
                reply="",
            )

        if result.requires_confirmation:
            return AIAgentConversationReply(
                handled=True,
                reply=(
                    "The requested plan can change system state "
                    "and requires confirmation. Reply 'confirm' "
                    "to continue or 'cancel' to discard it."
                ),
            )

        report = self._report_builder.build(result)

        return AIAgentConversationReply(
            handled=True,
            reply=self._format_report(report.summary, report.lines),
        )

    async def handle_pending(
        self,
        text: str,
    ) -> AIAgentConversationReply:
        normalized = text.strip().casefold()

        if normalized in {
            "cancel",
            "ยกเลิก",
            "ไม่เอา",
        }:
            cancelled = self._runtime.cancel_pending()

            return AIAgentConversationReply(
                handled=True,
                reply=(
                    "Pending AI plan cancelled."
                    if cancelled
                    else "There is no pending AI plan."
                ),
            )

        if normalized not in {
            "confirm",
            "confirmed",
            "yes",
            "ตกลง",
            "ยืนยัน",
        }:
            return AIAgentConversationReply(
                handled=True,
                reply=(
                    "A plan is waiting for confirmation. "
                    "Reply 'confirm' to execute it or "
                    "'cancel' to discard it."
                ),
            )

        result = await self._runtime.confirm_pending()
        report = self._report_builder.build(result)

        return AIAgentConversationReply(
            handled=True,
            reply=self._format_report(report.summary, report.lines),
        )

    @staticmethod
    def _format_report(
        summary: str,
        lines: tuple[str, ...],
    ) -> str:
        return "\n".join(
            (
                summary,
                *lines,
            )
        )
