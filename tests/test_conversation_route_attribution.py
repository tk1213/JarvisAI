from __future__ import annotations

import pytest

from jarvis.conversation.turn import (
    ConversationTurnLifecycle,
    ConversationTurnSource,
)


@pytest.mark.asyncio
async def test_handler_can_update_actual_turn_source() -> None:
    lifecycle = ConversationTurnLifecycle()

    async def handler() -> str:
        lifecycle.mark_source(
            ConversationTurnSource.NATIVE_TOOL
        )
        return "done"

    result = await lifecycle.run(
        user_text="hello",
        source=ConversationTurnSource.UNKNOWN,
        handler=handler,
    )

    assert result.source is ConversationTurnSource.NATIVE_TOOL
    assert lifecycle.active_source is None


@pytest.mark.asyncio
async def test_failure_keeps_actual_source() -> None:
    lifecycle = ConversationTurnLifecycle()

    async def handler() -> str:
        lifecycle.mark_source(
            ConversationTurnSource.PLANNER
        )
        raise RuntimeError(
            "failed"
        )

    with pytest.raises(
        RuntimeError,
        match="failed",
    ):
        await lifecycle.run(
            user_text="hello",
            source=ConversationTurnSource.UNKNOWN,
            handler=handler,
        )

    assert lifecycle.last_result is not None
    assert lifecycle.last_result.source is ConversationTurnSource.PLANNER
