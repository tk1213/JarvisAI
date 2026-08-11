from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class ConversationFailureKind(StrEnum):
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"
    AI_UPSTREAM = "ai_upstream"
    TOOL = "tool"
    PLANNER = "planner"
    CAPABILITY = "capability"
    MEMORY = "memory"
    INTERNAL = "internal"


class ConversationFallbackKind(StrEnum):
    NONE = "none"
    STANDARD_AI = "standard_ai"
    SAFE_MESSAGE = "safe_message"


@dataclass(slots=True, frozen=True)
class ConversationFailure:
    kind: ConversationFailureKind
    error_type: str
    message: str = ""
    retryable: bool = False


@dataclass(slots=True, frozen=True)
class ConversationFallback:
    kind: ConversationFallbackKind = ConversationFallbackKind.NONE
    reason: str | None = None

    @property
    def used(self) -> bool:
        return self.kind is not ConversationFallbackKind.NONE


@dataclass(slots=True, frozen=True)
class ConversationReliabilityOutcome:
    failure: ConversationFailure | None = None
    fallback: ConversationFallback = ConversationFallback()

    @property
    def failed(self) -> bool:
        return self.failure is not None

    @property
    def recovered(self) -> bool:
        return (
            self.failure is not None
            and self.fallback.used
        )


class ConversationFailureClassifier:
    """Map runtime exceptions into stable conversation failure categories."""

    def classify(
        self,
        exc: BaseException,
    ) -> ConversationFailure:
        if isinstance(
            exc,
            TimeoutError,
        ):
            return ConversationFailure(
                kind=ConversationFailureKind.TIMEOUT,
                error_type=type(exc).__name__,
                message=str(exc),
                retryable=True,
            )

        if isinstance(
            exc,
            KeyboardInterrupt,
        ):
            return ConversationFailure(
                kind=ConversationFailureKind.CANCELLED,
                error_type=type(exc).__name__,
                message=str(exc),
                retryable=False,
            )

        return ConversationFailure(
            kind=ConversationFailureKind.INTERNAL,
            error_type=type(exc).__name__,
            message=str(exc),
            retryable=False,
        )
