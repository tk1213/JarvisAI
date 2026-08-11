from __future__ import annotations

from unittest.mock import AsyncMock, Mock

import pytest

from jarvis.conversation.turn import ConversationTurnSource
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
async def test_actual_source_overrides_initial_prediction() -> None:
    manager = build_manager()

    async def legacy(
        text: str,
    ) -> str:
        del text
        manager._turn_lifecycle.mark_source(  # type: ignore[attr-defined]
            ConversationTurnSource.CAPABILITY
        )
        return "capability reply"

    manager._ask_legacy = legacy  # type: ignore[method-assign]

    reply = await manager.ask(
        "do something"
    )

    assert reply == "capability reply"
    assert manager.last_turn is not None
    assert manager.last_turn.source is ConversationTurnSource.CAPABILITY
