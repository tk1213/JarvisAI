from __future__ import annotations

from unittest.mock import AsyncMock, Mock

import pytest

from jarvis.tools.conversation_bridge import ToolCallingConversationBridge


@pytest.mark.asyncio
async def test_tool_bridge_marks_native_success() -> None:
    runner = Mock()
    runner.run = AsyncMock(
        return_value=Mock(
            text="native"
        )
    )
    fallback = Mock()
    fallback.ask = AsyncMock()

    bridge = ToolCallingConversationBridge(
        runner=runner,
        fallback_ai=fallback,
    )

    reply = await bridge.ask(
        text="hello"
    )

    assert reply == "native"
    assert bridge.last_used_fallback is False
    fallback.ask.assert_not_awaited()


@pytest.mark.asyncio
async def test_tool_bridge_marks_fallback_after_native_failure() -> None:
    runner = Mock()
    runner.run = AsyncMock(
        side_effect=RuntimeError(
            "native failed"
        )
    )
    fallback = Mock()
    fallback.ask = AsyncMock(
        return_value="fallback"
    )

    bridge = ToolCallingConversationBridge(
        runner=runner,
        fallback_ai=fallback,
    )

    reply = await bridge.ask(
        text="hello"
    )

    assert reply == "fallback"
    assert bridge.last_used_fallback is True
