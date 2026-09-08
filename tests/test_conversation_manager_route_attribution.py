from __future__ import annotations

from unittest.mock import AsyncMock, Mock

import pytest

from jarvis.conversation.turn import ConversationTurnSource
from jarvis.services.conversation_manager import ConversationManager
from jarvis.services.tool_router import ToolRouter


def build_manager() -> ConversationManager:
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

@pytest.mark.asyncio
async def test_music_request_uses_ai_route_not_legacy_plugin() -> None:
    memory = Mock()
    memory.save_message = AsyncMock()
    memory.save_turn = AsyncMock()
    memory.get_ai_history = AsyncMock(
        return_value=[]
    )

    manager = ConversationManager(
        ai=Mock(),
        memory=memory,
        router=ToolRouter(),
    )

    manager._handle_ai_route = AsyncMock(  # type: ignore[method-assign]
        return_value="AI reply"
    )

    reply = await manager._ask_legacy(  # type: ignore[attr-defined]
        "play music"
    )

    assert reply == "AI reply"

    manager._handle_ai_route.assert_awaited_once_with(  # type: ignore[attr-defined]
        "play music",
        voice_mode=False,
    )

@pytest.mark.asyncio
async def test_pending_route_precedence_is_agent_then_planner_then_smart_home() -> None:
    manager = build_manager()

    agent_reply = Mock(
        handled=True,
        reply="agent reply",
    )
    agent_bridge = Mock()
    agent_bridge.has_pending_plan = True
    agent_bridge.handle_pending = AsyncMock(
        return_value=agent_reply
    )

    planner_reply = Mock(
        handled=True,
        reply="planner reply",
    )
    planner_bridge = Mock()
    planner_bridge.has_pending_plan = True
    planner_bridge.handle_pending = AsyncMock(
        return_value=planner_reply
    )

    smart_home_pending = Mock()
    smart_home_pending.has_pending = True

    manager._ai_agent_bridge = agent_bridge  # type: ignore[attr-defined]
    manager._planner_bridge = planner_bridge  # type: ignore[attr-defined]
    manager._pending_smart_home_confirmation = (  # type: ignore[attr-defined]
        smart_home_pending
    )

    manager._handle_pending_smart_home_confirmation = AsyncMock(  # type: ignore[method-assign]
        return_value="smart home reply"
    )

    first_reply = await manager._ask_legacy(  # type: ignore[attr-defined]
        "confirm"
    )

    assert first_reply == "agent reply"
    agent_bridge.handle_pending.assert_awaited_once_with(
        "confirm"
    )
    planner_bridge.handle_pending.assert_not_awaited()
    manager._handle_pending_smart_home_confirmation.assert_not_awaited()  # type: ignore[attr-defined]

    agent_bridge.has_pending_plan = False

    second_reply = await manager._ask_legacy(  # type: ignore[attr-defined]
        "confirm"
    )

    assert second_reply == "planner reply"
    planner_bridge.handle_pending.assert_awaited_once_with(
        "confirm"
    )
    manager._handle_pending_smart_home_confirmation.assert_not_awaited()  # type: ignore[attr-defined]

    planner_bridge.has_pending_plan = False

    third_reply = await manager._ask_legacy(  # type: ignore[attr-defined]
        "confirm"
    )

    assert third_reply == "smart home reply"
    manager._handle_pending_smart_home_confirmation.assert_awaited_once_with(  # type: ignore[attr-defined]
        "confirm"
    )