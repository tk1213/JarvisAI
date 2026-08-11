from __future__ import annotations

import pytest

from jarvis.conversation.reliability import ConversationFailureKind
from jarvis.conversation.turn import (
    ConversationTurnLifecycle,
    ConversationTurnSource,
    ConversationTurnStatus,
)


@pytest.mark.asyncio
async def test_timeout_failure_is_attached_to_failed_turn() -> None:
    lifecycle = ConversationTurnLifecycle()

    async def handler() -> str:
        raise TimeoutError(
            "turn exceeded deadline"
        )

    with pytest.raises(
        TimeoutError,
        match="deadline",
    ):
        await lifecycle.run(
            user_text="hello",
            source=ConversationTurnSource.FALLBACK_AI,
            handler=handler,
        )

    result = lifecycle.last_result

    assert result is not None
    assert result.status is ConversationTurnStatus.FAILED
    assert result.reliability is not None
    assert result.reliability.failure is not None
    assert (
        result.reliability.failure.kind
        is ConversationFailureKind.TIMEOUT
    )
    assert result.reliability.failure.retryable is True


@pytest.mark.asyncio
async def test_internal_failure_is_attached_to_failed_turn() -> None:
    lifecycle = ConversationTurnLifecycle()

    async def handler() -> str:
        raise RuntimeError(
            "boom"
        )

    with pytest.raises(
        RuntimeError,
        match="boom",
    ):
        await lifecycle.run(
            user_text="hello",
            source=ConversationTurnSource.PLANNER,
            handler=handler,
        )

    result = lifecycle.last_result

    assert result is not None
    assert result.reliability is not None
    assert result.reliability.failure is not None
    assert (
        result.reliability.failure.kind
        is ConversationFailureKind.INTERNAL
    )
    assert result.source is ConversationTurnSource.PLANNER


@pytest.mark.asyncio
async def test_successful_turn_has_no_failure_outcome() -> None:
    lifecycle = ConversationTurnLifecycle()

    async def handler() -> str:
        return "ok"

    result = await lifecycle.run(
        user_text="hello",
        source=ConversationTurnSource.NATIVE_TOOL,
        handler=handler,
    )

    assert result.status is ConversationTurnStatus.COMPLETED
    assert result.reliability is None
