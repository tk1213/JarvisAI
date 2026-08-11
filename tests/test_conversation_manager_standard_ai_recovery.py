from __future__ import annotations

from unittest.mock import AsyncMock, Mock

import pytest

from jarvis.conversation.recovery import ConversationRecoveryService
from jarvis.conversation.reliability import (
    ConversationFailure,
    ConversationFailureKind,
    ConversationFallbackKind,
)
from jarvis.services.conversation_manager import ConversationManager


class ToolRecoveryService(ConversationRecoveryService):
    def plan(
        self,
        *,
        failure: ConversationFailure,
        attempts: int,
    ):
        return super().plan(
            failure=ConversationFailure(
                kind=ConversationFailureKind.TOOL,
                error_type=failure.error_type,
                retryable=True,
            ),
            attempts=attempts,
        )


@pytest.mark.asyncio
async def test_manager_standard_ai_recovery_failure_degrades_safely() -> None:
    memory = Mock()
    memory.save_message = AsyncMock()
    memory.get_ai_history = AsyncMock(
        return_value=[]
    )

    ai = Mock()
    ai.ask = AsyncMock(
        side_effect=RuntimeError(
            "fallback AI failed"
        )
    )

    manager = ConversationManager(
        ai=ai,
        memory=memory,
        router=Mock(),
        recovery_service=ToolRecoveryService(),
    )

    manager._ask_legacy = AsyncMock(  # type: ignore[method-assign]
        side_effect=RuntimeError(
            "primary failed"
        )
    )

    reply = await manager.ask(
        "recover"
    )

    assert reply == manager.recovery_safe_message

    execution = manager.last_recovery_execution

    assert execution is not None
    assert execution.fallback_kind is ConversationFallbackKind.SAFE_MESSAGE
    assert execution.fallback_error_type == "RuntimeError"
    ai.ask.assert_awaited_once()
