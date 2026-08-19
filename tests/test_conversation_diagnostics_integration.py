from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, Mock

import pytest

from jarvis.conversation.reliability import ConversationFailureKind
from jarvis.conversation.turn import (
    ConversationTurnSource,
    ConversationTurnStatus,
)
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


def test_no_turn_has_no_diagnostics_snapshot() -> None:
    manager = build_manager()

    assert manager.diagnostics_snapshot is None


@pytest.mark.asyncio
async def test_successful_turn_exposes_diagnostics_snapshot() -> None:
    manager = build_manager()

    manager._ask_legacy = AsyncMock(  # type: ignore[method-assign]
        return_value="ok"
    )

    reply = await manager.ask(
        "hello"
    )

    assert reply == "ok"

    snapshot = manager.diagnostics_snapshot

    assert snapshot is not None
    assert snapshot.turn.status is ConversationTurnStatus.COMPLETED
    assert snapshot.turn.duration_ms >= 0


@pytest.mark.asyncio
async def test_recovered_timeout_exposes_failure_diagnostics() -> None:
    manager = build_manager(
        timeout_seconds=0.01
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

    assert reply == manager.recovery_safe_message

    snapshot = manager.diagnostics_snapshot

    assert snapshot is not None
    assert snapshot.turn.status is ConversationTurnStatus.FAILED
    assert snapshot.reliability.failure_kind is ConversationFailureKind.TIMEOUT
    assert snapshot.reliability.retryable is True
    assert snapshot.recovery.executed is True


@pytest.mark.asyncio
async def test_actual_route_is_preserved_in_snapshot() -> None:
    manager = build_manager()

    async def routed(
        text: str,
    ) -> str:
        del text
        manager._turn_lifecycle.mark_source(  # type: ignore[attr-defined]
            ConversationTurnSource.FALLBACK_AI
        )
        return "reply"

    manager._ask_legacy = routed  # type: ignore[method-assign]

    await manager.ask(
        "hello"
    )

    snapshot = manager.diagnostics_snapshot

    assert snapshot is not None
    assert snapshot.turn.source is ConversationTurnSource.FALLBACK_AI
