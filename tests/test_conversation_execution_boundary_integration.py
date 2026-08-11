from __future__ import annotations

import asyncio

import pytest

from jarvis.conversation.execution_boundary import (
    ConversationExecutionBoundary,
    ConversationExecutionPolicy,
)
from jarvis.conversation.reliability import ConversationFailureKind
from jarvis.conversation.turn import (
    ConversationTurnLifecycle,
    ConversationTurnSource,
)


@pytest.mark.asyncio
async def test_timeout_boundary_flows_into_turn_failure_classification() -> None:
    lifecycle = ConversationTurnLifecycle()
    boundary = ConversationExecutionBoundary(
        ConversationExecutionPolicy(
            timeout_seconds=0.01
        )
    )

    async def slow_handler() -> str:
        await asyncio.sleep(
            1.0
        )
        return "late"

    with pytest.raises(
        TimeoutError
    ):
        await lifecycle.run(
            user_text="slow turn",
            source=ConversationTurnSource.FALLBACK_AI,
            handler=lambda: boundary.run(
                slow_handler
            ),
        )

    result = lifecycle.last_result

    assert result is not None
    assert result.reliability is not None
    assert result.reliability.failure is not None
    assert (
        result.reliability.failure.kind
        is ConversationFailureKind.TIMEOUT
    )
    assert result.reliability.failure.retryable is True


@pytest.mark.asyncio
async def test_external_cancellation_is_not_converted_to_timeout() -> None:
    boundary = ConversationExecutionBoundary(
        ConversationExecutionPolicy(
            timeout_seconds=5.0
        )
    )

    started = asyncio.Event()

    async def handler() -> str:
        started.set()
        await asyncio.sleep(
            10.0
        )
        return "never"

    task = asyncio.create_task(
        boundary.run(
            handler
        )
    )

    await started.wait()
    task.cancel()

    with pytest.raises(
        asyncio.CancelledError
    ):
        await task
