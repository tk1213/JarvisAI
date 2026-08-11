from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from jarvis.conversation.reliability import (
    ConversationFallbackKind,
    ConversationReliabilityOutcome,
)


@dataclass(slots=True, frozen=True)
class ConversationRecoveryExecutionResult:
    reply: str
    executed: bool
    fallback_kind: ConversationFallbackKind
    attempts_used: int
    fallback_error_type: str | None = None

    @property
    def used_safe_message(self) -> bool:
        return self.fallback_kind is ConversationFallbackKind.SAFE_MESSAGE

    @property
    def used_standard_ai(self) -> bool:
        return self.fallback_kind is ConversationFallbackKind.STANDARD_AI

    @property
    def fallback_failed(self) -> bool:
        return self.fallback_error_type is not None


class ConversationRecoveryExecutor:
    """Execute one bounded recovery action without recursive recovery."""

    def __init__(
        self,
        *,
        safe_message: str = (
            "ขออภัยครับ ตอนนี้ผมไม่สามารถดำเนินการคำขอนี้ได้อย่างปลอดภัย "
            "กรุณาลองใหม่อีกครั้ง"
        ),
    ) -> None:
        self._safe_message = safe_message

    @property
    def safe_message(self) -> str:
        return self._safe_message

    async def execute(
        self,
        *,
        outcome: ConversationReliabilityOutcome,
        attempts_used: int,
        standard_ai_fallback: Callable[[], Awaitable[str]] | None = None,
    ) -> ConversationRecoveryExecutionResult:
        fallback = outcome.fallback

        if not outcome.recovered:
            return ConversationRecoveryExecutionResult(
                reply="",
                executed=False,
                fallback_kind=ConversationFallbackKind.NONE,
                attempts_used=attempts_used,
            )

        if fallback.kind is ConversationFallbackKind.SAFE_MESSAGE:
            return ConversationRecoveryExecutionResult(
                reply=self._safe_message,
                executed=True,
                fallback_kind=fallback.kind,
                attempts_used=attempts_used,
            )

        if fallback.kind is ConversationFallbackKind.STANDARD_AI:
            if standard_ai_fallback is None:
                return ConversationRecoveryExecutionResult(
                    reply=self._safe_message,
                    executed=True,
                    fallback_kind=ConversationFallbackKind.SAFE_MESSAGE,
                    attempts_used=attempts_used,
                )

            try:
                reply = await standard_ai_fallback()
            except (RuntimeError, TimeoutError) as exc:
                return ConversationRecoveryExecutionResult(
                    reply=self._safe_message,
                    executed=True,
                    fallback_kind=ConversationFallbackKind.SAFE_MESSAGE,
                    attempts_used=attempts_used,
                    fallback_error_type=type(exc).__name__,
                )

            return ConversationRecoveryExecutionResult(
                reply=reply,
                executed=True,
                fallback_kind=ConversationFallbackKind.STANDARD_AI,
                attempts_used=attempts_used,
            )