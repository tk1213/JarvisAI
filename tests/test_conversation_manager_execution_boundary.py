from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, Mock

import pytest

from jarvis.conversation.reliability import ConversationFailureKind
from jarvis.conversation.turn import ConversationTurnStatus
from jarvis.services.conversation_manager import ConversationManager


def build_manager(
    timeout_seconds: float = 1.0,
) -> ConversationManager:
    memory = Mock()
    memory.save_message = AsyncMock()
    memory.save_turn = AsyncMock()
    memory.get_ai_history = AsyncMock(
        return_value=[]
    )

    return ConversationManager(
        ai=Mock(),
        memory=memory,
        router=Mock(),
        conversation_timeout_seconds=timeout_seconds,
    )


@pytest.mark.asyncio
async def test_success_reply_preserved() -> None:
    manager = build_manager()

    manager._ask_legacy = AsyncMock(  # type: ignore[method-assign]
        return_value="ready"
    )

    reply = await manager.ask(
        "hello"
    )

    assert reply == "ready"
    assert manager.last_turn is not None
    assert manager.last_turn.status is ConversationTurnStatus.COMPLETED


@pytest.mark.asyncio
async def test_timeout_is_classified_traced_and_recovered() -> None:
    manager = build_manager(
        0.01
    )

    async def slow(
        text: str,
    ) -> str:
        del text
        await asyncio.sleep(
            1
        )
        return "late"

    manager._ask_legacy = slow  # type: ignore[method-assign]

    reply = await manager.ask(
        "slow"
    )

    assert reply == manager.recovery_safe_message

    result = manager.last_turn

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
async def test_external_cancellation_propagates() -> None:
    manager = build_manager(
        5
    )

    started = asyncio.Event()

    async def slow(
        text: str,
    ) -> str:
        del text
        started.set()

        await asyncio.sleep(
            10
        )

        return "late"

    manager._ask_legacy = slow  # type: ignore[method-assign]

    task = asyncio.create_task(
        manager.ask(
            "cancel"
        )
    )

    await started.wait()
    task.cancel()

    with pytest.raises(
        asyncio.CancelledError
    ):
        await task


def test_default_constructor_is_backward_compatible() -> None:
    memory = Mock()

    manager = ConversationManager(
        ai=Mock(),
        memory=memory,
        router=Mock(),
    )

    assert manager.conversation_timeout_seconds == 60.0
