from __future__ import annotations

import asyncio

import pytest

from jarvis.core.event_bus import EventBus
from jarvis.core.events import Event


@pytest.mark.asyncio
async def test_publish_calls_subscribed_handler() -> None:
    bus = EventBus()
    received: list[Event] = []

    async def handler(event: Event) -> None:
        received.append(event)

    bus.subscribe(
        "test.message",
        handler,
    )

    event = Event(
        name="test.message",
        payload={"message": "Hello Jarvis"},
    )

    await bus.publish(event)

    assert received == [event]


@pytest.mark.asyncio
async def test_unsubscribe_stops_handler_delivery() -> None:
    bus = EventBus()
    received: list[Event] = []

    async def handler(event: Event) -> None:
        received.append(event)

    bus.subscribe(
        "test.message",
        handler,
    )

    bus.unsubscribe(
        "test.message",
        handler,
    )

    await bus.publish(
        Event(
            name="test.message",
            payload={},
        )
    )

    assert received == []


@pytest.mark.asyncio
async def test_publish_isolates_handler_failure() -> None:
    bus = EventBus()
    completed: list[str] = []

    async def failing_handler(
        event: Event,
    ) -> None:
        del event
        raise RuntimeError(
            "handler failed"
        )

    async def successful_handler(
        event: Event,
    ) -> None:
        del event
        await asyncio.sleep(0)
        completed.append(
            "successful"
        )

    bus.subscribe(
        "test.message",
        failing_handler,
    )

    bus.subscribe(
        "test.message",
        successful_handler,
    )

    await bus.publish(
        Event(
            name="test.message",
            payload={},
        )
    )

    assert completed == [
        "successful"
    ]


@pytest.mark.asyncio
async def test_publish_propagates_handler_cancellation() -> None:
    bus = EventBus()

    async def cancelled_handler(
        event: Event,
    ) -> None:
        del event
        raise asyncio.CancelledError

    bus.subscribe(
        "test.message",
        cancelled_handler,
    )

    with pytest.raises(
        asyncio.CancelledError
    ):
        await bus.publish(
            Event(
                name="test.message",
                payload={},
            )
        )


@pytest.mark.asyncio
async def test_publish_propagates_caller_cancellation() -> None:
    bus = EventBus()
    started = asyncio.Event()
    cancelled = asyncio.Event()

    async def slow_handler(
        event: Event,
    ) -> None:
        del event
        started.set()

        try:
            await asyncio.sleep(60)
        except asyncio.CancelledError:
            cancelled.set()
            raise

    bus.subscribe(
        "test.message",
        slow_handler,
    )

    task = asyncio.create_task(
        bus.publish(
            Event(
                name="test.message",
                payload={},
            )
        )
    )

    await started.wait()
    task.cancel()

    with pytest.raises(asyncio.CancelledError):
        await task

    assert cancelled.is_set()