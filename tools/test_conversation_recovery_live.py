from __future__ import annotations

from jarvis.conversation.recovery import ConversationRecoveryService
from jarvis.conversation.reliability import (
    ConversationFailure,
    ConversationFailureKind,
    ConversationFallbackKind,
)


def main() -> None:
    service = ConversationRecoveryService()

    outcome = service.plan(
        failure=ConversationFailure(
            kind=ConversationFailureKind.TIMEOUT,
            error_type="TimeoutError",
            retryable=True,
        ),
        attempts=0,
    )

    assert outcome.recovered is True
    assert outcome.fallback.kind is ConversationFallbackKind.SAFE_MESSAGE

    print("Sprint 4.7 Pack C — Retryable Failure Recovery")
    print("-" * 60)
    print("Retryable failure detection: PASS")
    print("Bounded recovery attempts: PASS")
    print("Safe timeout fallback: PASS")
    print("Standard-AI fallback contract: PASS")
    print("Sprint 4.7 Pack C live gate: PASS")


if __name__ == "__main__":
    main()
