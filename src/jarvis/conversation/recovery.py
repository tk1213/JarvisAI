from __future__ import annotations

from dataclasses import dataclass

from jarvis.conversation.reliability import (
    ConversationFailure,
    ConversationFailureKind,
    ConversationFallback,
    ConversationFallbackKind,
    ConversationReliabilityOutcome,
)


@dataclass(slots=True, frozen=True)
class ConversationRecoveryPolicy:
    max_recovery_attempts: int = 1

    def __post_init__(self) -> None:
        if self.max_recovery_attempts < 0:
            raise ValueError(
                "max_recovery_attempts cannot be negative."
            )

    def can_recover(
        self,
        *,
        failure: ConversationFailure,
        attempts: int,
    ) -> bool:
        return (
            failure.retryable
            and attempts < self.max_recovery_attempts
        )

    def fallback_for(
        self,
        *,
        failure: ConversationFailure,
    ) -> ConversationFallback:
        if failure.kind is ConversationFailureKind.TIMEOUT:
            return ConversationFallback(
                kind=ConversationFallbackKind.SAFE_MESSAGE,
                reason="conversation_timeout",
            )

        if failure.kind in {
            ConversationFailureKind.AI_UPSTREAM,
            ConversationFailureKind.TOOL,
        }:
            return ConversationFallback(
                kind=ConversationFallbackKind.STANDARD_AI,
                reason=failure.kind.value,
            )

        return ConversationFallback(
            kind=ConversationFallbackKind.SAFE_MESSAGE,
            reason=failure.kind.value,
        )


class ConversationRecoveryService:
    def __init__(
        self,
        policy: ConversationRecoveryPolicy | None = None,
    ) -> None:
        self._policy = (
            policy
            if policy is not None
            else ConversationRecoveryPolicy()
        )

    @property
    def policy(self) -> ConversationRecoveryPolicy:
        return self._policy

    def plan(
        self,
        *,
        failure: ConversationFailure,
        attempts: int,
    ) -> ConversationReliabilityOutcome:
        if not self._policy.can_recover(
            failure=failure,
            attempts=attempts,
        ):
            return ConversationReliabilityOutcome(
                failure=failure,
            )

        return ConversationReliabilityOutcome(
            failure=failure,
            fallback=self._policy.fallback_for(
                failure=failure
            ),
        )
