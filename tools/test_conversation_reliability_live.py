from __future__ import annotations

from jarvis.conversation.reliability import (
    ConversationFailureClassifier,
    ConversationFailureKind,
    ConversationFallback,
    ConversationFallbackKind,
    ConversationReliabilityOutcome,
)


def main() -> None:
    failure = ConversationFailureClassifier().classify(
        TimeoutError(
            "simulated timeout"
        )
    )

    fallback = ConversationFallback(
        kind=ConversationFallbackKind.STANDARD_AI,
        reason="fallback after timeout",
    )

    outcome = ConversationReliabilityOutcome(
        failure=failure,
        fallback=fallback,
    )

    assert failure.kind is ConversationFailureKind.TIMEOUT
    assert failure.retryable is True
    assert fallback.used is True
    assert outcome.recovered is True

    print("Sprint 4.6 Pack A — Failure Classification & Fallback Contract")
    print("-" * 60)
    print("Failure taxonomy: PASS")
    print("Timeout classification: PASS")
    print("Fallback contract: PASS")
    print("Recovery outcome: PASS")
    print("Sprint 4.6 Pack A live gate: PASS")


if __name__ == "__main__":
    main()
