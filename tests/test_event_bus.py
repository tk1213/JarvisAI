from __future__ import annotations

import asyncio

from jarvis.core.event_bus import event_bus
from jarvis.core.events import Event


async def on_test_event(event: Event) -> None:
    print(f"Event name: {event.name}")
    print(f"Event ID: {event.event_id}")
    print(f"Timestamp: {event.timestamp}")
    print(f"Payload: {event.payload}")


async def main() -> None:
    event_bus.clear()

    event_bus.subscribe(
        event_name="test.message",
        handler=on_test_event,
    )

    await event_bus.publish(
        Event(
            name="test.message",
            payload={
                "message": "Hello Jarvis",
            },
        )
    )

    event_bus.unsubscribe(
        event_name="test.message",
        handler=on_test_event,
    )


if __name__ == "__main__":
    asyncio.run(main())