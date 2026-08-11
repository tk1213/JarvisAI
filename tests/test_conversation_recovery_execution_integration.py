from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, Mock

import pytest

from jarvis.conversation.recovery_execution import ConversationRecoveryExecutor
from jarvis.services.conversation_manager import ConversationManager


def build_manager(
    *,
    timeout_seconds: float = 1.0,
    safe_message: str = "safe",
) -> ConversationManager:
    memory = Mock()
    memory.save_message = AsyncMock()
    memory.get_ai_history = AsyncMock(
        return_value=[]
    )

    return ConversationManager(
        ai=Mock(),
        memory=memory,
        router=Mock(),
        conversation_timeout_seconds=timeout_seconds,
        recovery_executor=ConversationRecoveryExecutor(
            safe_message=safe_message
        ),
    )


@pytest.mark.asyncio
async def test_timeout_returns_safe_message() -> None:
    manager = build_manager(
        timeout_seconds=0.01,
        safe_message="safe timeout",
    )

    async def slow(
        text: str,
    ) -> str:
        del text
        await asyncio.sleep(
            1
        )
        return "late"

    manager._ask_legacy = slow  # type: ignore[method-assign]

    reply = await manager.ask(
        "slow"
    )

    assert reply == "safe timeout"


@pytest.mark.asyncio
async def test_non_retryable_failure_still_raises() -> None:
    manager = build_manager()

    manager._ask_legacy = AsyncMock(  # type: ignore[method-assign]
        side_effect=RuntimeError(
            "boom"
        )
    )

    with pytest.raises(
        RuntimeError,
        match="boom",
    ):
        await manager.ask(
            "fail"
        )


@pytest.mark.asyncio
async def test_success_path_is_unchanged() -> None:
    manager = build_manager()

    manager._ask_legacy = AsyncMock(  # type: ignore[method-assign]
        return_value="ok"
    )

    assert await manager.ask(
        "hello"
    ) == "ok"


def test_recovery_safe_message_is_observable() -> None:
    manager = build_manager(
        safe_message="visible safe message"
    )

    assert (
        manager.recovery_safe_message
        == "visible safe message"
    )
