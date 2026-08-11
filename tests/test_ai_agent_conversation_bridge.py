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


def make_result(
    status: AIAgentRunStatus,
) -> AIAgentRunResult:
    return AIAgentRunResult(
        status=status,
        preview=None,
        execution=None,
        reflection=None,
        memory_record=None,
    )


@pytest.mark.asyncio
async def test_bridge_falls_back_when_no_plan() -> None:
    runtime = Mock()
    runtime.run = AsyncMock(
        return_value=make_result(
            AIAgentRunStatus.NO_PLAN
        )
    )

    reply = await AIAgentConversationBridge(
        runtime
    ).handle_ai_request(
        "hello"
    )

    assert reply.handled is False
    assert reply.reply == ""


@pytest.mark.asyncio
async def test_bridge_requests_confirmation() -> None:
    result = make_result(
        AIAgentRunStatus.CONFIRMATION_REQUIRED
    )

    runtime = Mock()
    runtime.run = AsyncMock(
        return_value=result
    )

    reply = await AIAgentConversationBridge(
        runtime
    ).handle_ai_request(
        "turn on light"
    )

    assert reply.handled is True
    assert "requires confirmation" in reply.reply


@pytest.mark.asyncio
async def test_bridge_cancels_pending_plan() -> None:
    runtime = Mock()
    runtime.cancel_pending.return_value = True

    reply = await AIAgentConversationBridge(
        runtime
    ).handle_pending(
        "cancel"
    )

    assert reply.handled is True
    assert "cancelled" in reply.reply
