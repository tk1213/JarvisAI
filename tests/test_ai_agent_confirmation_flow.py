from __future__ import annotations

from unittest.mock import AsyncMock, Mock

import pytest

from jarvis.agent.conversation_bridge import (
    AIAgentConversationBridge,
)
from jarvis.agent.runtime import (
    AIAgentRunResult,
    AIAgentRunStatus,
)


def make_completed_result() -> AIAgentRunResult:
    return AIAgentRunResult(
        status=AIAgentRunStatus.COMPLETED,
        preview=None,
        execution=None,
        reflection=None,
        memory_record=None,
    )


@pytest.mark.asyncio
async def test_pending_unknown_reply_does_not_execute() -> None:
    runtime = Mock()
    runtime.confirm_pending = AsyncMock()

    reply = await AIAgentConversationBridge(
        runtime
    ).handle_pending(
        "maybe"
    )

    assert reply.handled is True
    assert "waiting for confirmation" in reply.reply
    runtime.confirm_pending.assert_not_awaited()


@pytest.mark.asyncio
async def test_pending_confirm_executes_once() -> None:
    runtime = Mock()
    runtime.confirm_pending = AsyncMock(
        return_value=make_completed_result()
    )

    reply = await AIAgentConversationBridge(
        runtime
    ).handle_pending(
        "confirm"
    )

    assert reply.handled is True
    runtime.confirm_pending.assert_awaited_once()


@pytest.mark.asyncio
async def test_pending_cancel_never_executes() -> None:
    runtime = Mock()
    runtime.cancel_pending.return_value = True
    runtime.confirm_pending = AsyncMock()

    reply = await AIAgentConversationBridge(
        runtime
    ).handle_pending(
        "cancel"
    )

    assert reply.handled is True
    assert "cancelled" in reply.reply
    runtime.confirm_pending.assert_not_awaited()
