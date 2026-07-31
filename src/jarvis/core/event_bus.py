from __future__ import annotations

import asyncio
from collections import defaultdict
from collections.abc import Awaitable, Callable

from jarvis.core.events import Event

EventHandler = Callable[[Event], Awaitable[None]]


class EventBus:
    def __init__(self) -> None:
        self._handlers: dict[str, list[EventHandler]] = defaultdict(list)

    def subscribe(
        self,
        event_name: str,
        handler: EventHandler,
    ) -> None:
        if handler not in self._handlers[event_name]:
            self._handlers[event_name].append(handler)

    def unsubscribe(
        self,
        event_name: str,
        handler: EventHandler,
    ) -> None:
        handlers = self._handlers.get(event_name)

        if not handlers:
            return

        if handler in handlers:
            handlers.remove(handler)

        if not handlers:
            self._handlers.pop(event_name, None)

    async def publish(
        self,
        event: Event,
    ) -> None:
        handlers = self._handlers.get(event.name)

        if not handlers:
            return

        await asyncio.gather(
            *(handler(event) for handler in handlers)
        )

    def clear(self) -> None:
        self._handlers.clear()


event_bus = EventBus()