from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, Mock

import pytest

from jarvis.conversation.reliability import ConversationFallbackKind
from jarvis.services.conversation_manager import ConversationManager


def build_manager(
    *,
    timeout_seconds: float = 1.0,
) -> ConversationManager:
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
        conversation_timeout_seconds=timeout_seconds,
    )


@pytest.mark.asyncio
async def test_timeout_exposes_safe_recovery_plan() -> None:
    manager = build_manager(
        timeout_seconds=0.01
    )

    async def slow(
        text: str,
    ) -> str:
        del text
        await asyncio.sleep(1)
        return "late"

    manager._ask_legacy = slow  # type: ignore[method-assign]

    reply = await manager.ask(
        "slow"
    )

    assert reply == manager.recovery_safe_message

    plan = manager.recovery_plan_for_last_turn()

    assert plan is not None
    assert plan.recovered is True
    assert plan.fallback.kind is ConversationFallbackKind.SAFE_MESSAGE


@pytest.mark.asyncio
async def test_recovery_plan_is_bounded() -> None:
    manager = build_manager(
        timeout_seconds=0.01
    )

    async def slow(
        text: str,
    ) -> str:
        del text
        await asyncio.sleep(1)
        return "late"

    manager._ask_legacy = slow  # type: ignore[method-assign]

    reply = await manager.ask(
        "slow"
    )

    assert reply == manager.recovery_safe_message

    exhausted = manager.recovery_plan_for_last_turn(
        attempts=1
    )

    assert exhausted is not None
    assert exhausted.recovered is False


def test_default_recovery_limit_is_observable() -> None:
    manager = build_manager()

    assert manager.max_recovery_attempts == 1


def test_no_failure_has_no_recovery_plan() -> None:
    manager = build_manager()

    assert manager.recovery_plan_for_last_turn() is None
