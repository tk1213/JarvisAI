from __future__ import annotations

from unittest.mock import AsyncMock, Mock

import pytest

from jarvis.services.conversation_manager import ConversationManager


@pytest.mark.asyncio
async def test_manager_exposes_unified_health_report() -> None:
    memory = Mock()
    memory.save_message = AsyncMock()
    memory.save_turn = AsyncMock()
    memory.get_ai_history = AsyncMock(return_value=[])

    manager = ConversationManager(
        ai=Mock(),
        memory=memory,
        router=Mock(),
    )
    manager._ask_legacy = AsyncMock(  # type: ignore[method-assign]
        return_value="ok"
    )

    await manager.ask("hello")

    report = manager.health_report

    assert report.operational.total_turns == 1
    assert report.operational.completed_turns == 1
    assert report.latest_turn is not None
    assert report.latest_turn.turn.turn_id == report.operational.last_turn_id
