from __future__ import annotations

import asyncio

import pytest

from jarvis.core.event_bus import event_bus
from jarvis.core.events import Event
from jarvis.core.session import SessionState
from jarvis.services.session_manager import SessionManager


@pytest.fixture(autouse=True)
def clear_event_bus() -> None:
    event_bus.clear()
    yield
    event_bus.clear()


@pytest.mark.asyncio
async def test_set_state_updates_state() -> None:
    session = SessionManager()

    await session.set_state(
        SessionState.STARTING
    )

    assert session.state is SessionState.STARTING


@pytest.mark.asyncio
async def test_set_state_publishes_state_change() -> None:
    session = SessionManager()
    received: list[Event] = []

    async def handler(event: Event) -> None:
        received.append(event)

    event_bus.subscribe(
        "session.state_changed",
        handler,
    )

    await session.set_state(
        SessionState.IDLE
    )

    assert len(received) == 1
    assert received[0].payload == {
        "old": SessionState.OFFLINE.value,
        "new": SessionState.IDLE.value,
    }


@pytest.mark.asyncio
async def test_set_state_does_not_publish_when_state_is_unchanged() -> None:
    session = SessionManager()
    received: list[Event] = []

    async def handler(event: Event) -> None:
        received.append(event)

    event_bus.subscribe(
        "session.state_changed",
        handler,
    )

    await session.set_state(
        SessionState.OFFLINE
    )

    assert received == []


@pytest.mark.asyncio
async def test_state_transition_survives_observer_failure() -> None:
    session = SessionManager()

    async def failing_handler(
        event: Event,
    ) -> None:
        del event
        raise RuntimeError(
            "observer failed"
        )

    event_bus.subscribe(
        "session.state_changed",
        failing_handler,
    )

    await session.set_state(
        SessionState.IDLE
    )

    assert session.state is SessionState.IDLE

@pytest.mark.asyncio
async def test_state_transition_remains_committed_when_publish_is_cancelled() -> None:
    session = SessionManager()
    handler_entered = asyncio.Event()

    async def blocking_handler(
        event: Event,
    ) -> None:
        del event
        handler_entered.set()
        await asyncio.Future()

    event_bus.subscribe(
        "session.state_changed",
        blocking_handler,
    )

    task = asyncio.create_task(
        session.set_state(
            SessionState.IDLE
        )
    )

    await handler_entered.wait()

    assert session.state is SessionState.IDLE

    task.cancel()

    with pytest.raises(
        asyncio.CancelledError,
    ):
        await task

    assert session.state is SessionState.IDLE 

@pytest.mark.asyncio
async def test_state_transition_remains_committed_when_handler_is_cancelled() -> None:
    session = SessionManager()

    async def cancelling_handler(
        event: Event,
    ) -> None:
        del event
        raise asyncio.CancelledError

    event_bus.subscribe(
        "session.state_changed",
        cancelling_handler,
    )

    with pytest.raises(
        asyncio.CancelledError,
    ):
        await session.set_state(
            SessionState.IDLE
        )

    assert session.state is SessionState.IDLE