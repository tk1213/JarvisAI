from __future__ import annotations

from unittest.mock import AsyncMock, Mock

import pytest

from jarvis.conversation.turn import ConversationTurnStatus
from jarvis.services.conversation_manager import ConversationManager


def build_manager() -> ConversationManager:
    memory = Mock()
    memory.save_message = AsyncMock()
    memory.get_ai_history = AsyncMock(return_value=[])

    return ConversationManager(
        ai=Mock(),
        memory=memory,
        router=Mock(),
    )


@pytest.mark.asyncio
async def test_empty_ask_records_empty_turn() -> None:
    manager = build_manager()

    assert await manager.ask("   ") == ""
    assert manager.last_turn is not None
    assert manager.last_turn.status is ConversationTurnStatus.EMPTY


@pytest.mark.asyncio
async def test_ask_preserves_reply_and_records_turn() -> None:
    manager = build_manager()
    manager._ask_legacy = AsyncMock(return_value="same reply")

    assert await manager.ask("hello") == "same reply"
    assert manager.last_turn is not None
    assert manager.last_turn.status is ConversationTurnStatus.COMPLETED
    assert manager.last_turn.reply == "same reply"


@pytest.mark.asyncio
async def test_ask_records_failure_before_reraising() -> None:
    manager = build_manager()
    manager._ask_legacy = AsyncMock(side_effect=RuntimeError("boom"))

    with pytest.raises(RuntimeError, match="boom"):
        await manager.ask("hello")

    assert manager.last_turn is not None
    assert manager.last_turn.status is ConversationTurnStatus.FAILED
    assert manager.last_turn.error_type == "RuntimeError"
