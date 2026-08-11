from __future__ import annotations

from unittest.mock import AsyncMock, Mock

import pytest

from jarvis.conversation.turn import ConversationTurnStatus
from jarvis.services.conversation_manager import ConversationManager


def build_manager() -> ConversationManager:
    memory = Mock()
    memory.save_message = AsyncMock()
    memory.get_ai_history = AsyncMock(
        return_value=[]
    )

    return ConversationManager(
        ai=Mock(),
        memory=memory,
        router=Mock(),
    )


@pytest.mark.asyncio
async def test_wrapper_calls_legacy_path() -> None:
    manager = build_manager()

    legacy = AsyncMock(
        return_value="same reply"
    )
    manager._ask_legacy = legacy  # type: ignore[method-assign]

    reply = await manager.ask(
        "hello"
    )

    assert reply == "same reply"
    legacy.assert_awaited_once_with(
        "hello"
    )


@pytest.mark.asyncio
async def test_wrapper_records_completed_turn() -> None:
    manager = build_manager()
    manager._ask_legacy = AsyncMock(  # type: ignore[method-assign]
        return_value="reply"
    )

    await manager.ask(
        "hello"
    )

    assert manager.last_turn is not None
    assert manager.last_turn.status is ConversationTurnStatus.COMPLETED
    assert manager.last_turn.reply == "reply"


@pytest.mark.asyncio
async def test_wrapper_records_empty_turn() -> None:
    manager = build_manager()

    reply = await manager.ask(
        "   "
    )

    assert reply == ""
    assert manager.last_turn is not None
    assert manager.last_turn.status is ConversationTurnStatus.EMPTY
