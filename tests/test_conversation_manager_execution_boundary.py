from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, Mock

import pytest

from jarvis.conversation.reliability import ConversationFailureKind
from jarvis.conversation.turn import ConversationTurnStatus
from jarvis.core.event_bus import event_bus
from jarvis.services.conversation_manager import ConversationManager


def build_manager(
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
async def test_success_reply_preserved() -> None:
    manager = build_manager()

    manager._ask_legacy = AsyncMock(  # type: ignore[method-assign]
        return_value="ready"
    )

    reply = await manager.ask(
        "hello"
    )

    assert reply == "ready"
    assert manager.last_turn is not None
    assert manager.last_turn.status is ConversationTurnStatus.COMPLETED


@pytest.mark.asyncio
async def test_timeout_is_classified_traced_and_recovered() -> None:
    manager = build_manager(
        0.01
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

    result = manager.last_turn

    assert result is not None
    assert result.status is ConversationTurnStatus.FAILED
    assert result.reliability is not None
    assert result.reliability.failure is not None
    assert (
        result.reliability.failure.kind
        is ConversationFailureKind.TIMEOUT
    )
    assert result.reliability.failure.retryable is True


@pytest.mark.asyncio
async def test_external_cancellation_propagates() -> None:
    manager = build_manager(
        5
    )

    started = asyncio.Event()

    async def slow(
        text: str,
    ) -> str:
        del text
        started.set()

        await asyncio.sleep(
            10
        )

        return "late"

    manager._ask_legacy = slow  # type: ignore[method-assign]

    task = asyncio.create_task(
        manager.ask(
            "cancel"
        )
    )

    await started.wait()
    task.cancel()

    with pytest.raises(
        asyncio.CancelledError
    ):
        await task


def test_default_constructor_is_backward_compatible() -> None:
    memory = Mock()

    manager = ConversationManager(
        ai=Mock(),
        memory=memory,
        router=Mock(),
    )

    assert manager.conversation_timeout_seconds == 60.0

@pytest.mark.asyncio
async def test_memory_persistence_cancellation_does_not_complete_turn(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    manager = build_manager()

    manager._memory.save_turn = AsyncMock(  # type: ignore[attr-defined]
        side_effect=asyncio.CancelledError()
    )

    published: list[str] = []

    async def capture_publish(event: object) -> None:
        name = getattr(event, "name", None)

        if isinstance(name, str):
            published.append(name)

    monkeypatch.setattr(
        event_bus,
        "publish",
        capture_publish,
    )

    async def persist_reply(
        text: str,
    ) -> str:
        await manager._save_conversation(
            user_text=text,
            reply="generated reply",
            tool="ai",
        )

        return "generated reply"

    manager._ask_legacy = persist_reply  # type: ignore[method-assign]

    with pytest.raises(
        asyncio.CancelledError,
    ):
        await manager.ask(
            "cancel during persistence"
        )

    assert manager.last_turn is None
    assert manager._turn_lifecycle.active_source is None
    assert "conversation.response" not in published

@pytest.mark.asyncio
async def test_caller_cancellation_during_memory_persistence_clears_turn_state(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    manager = build_manager()

    persistence_started = asyncio.Event()
    release_persistence = asyncio.Event()

    async def blocking_save_turn(
        *,
        user_content: str,
        assistant_content: str,
    ) -> None:
        del user_content, assistant_content
        persistence_started.set()
        await release_persistence.wait()

    manager._memory.save_turn = blocking_save_turn  # type: ignore[attr-defined]

    published: list[str] = []

    async def capture_publish(event: object) -> None:
        name = getattr(event, "name", None)

        if isinstance(name, str):
            published.append(name)

    monkeypatch.setattr(
        event_bus,
        "publish",
        capture_publish,
    )

    async def persist_reply(
        text: str,
    ) -> str:
        await manager._save_conversation(
            user_text=text,
            reply="generated reply",
            tool="ai",
        )

        return "generated reply"

    manager._ask_legacy = persist_reply  # type: ignore[method-assign]

    task = asyncio.create_task(
        manager.ask(
            "cancel while saving"
        )
    )

    await persistence_started.wait()

    task.cancel()

    with pytest.raises(
        asyncio.CancelledError,
    ):
        await task

    assert manager.last_turn is None
    assert manager._turn_lifecycle.active_source is None
    assert "conversation.response" not in published