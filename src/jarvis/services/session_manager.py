from __future__ import annotations

from jarvis.core.event_bus import event_bus
from jarvis.core.events import Event
from jarvis.core.session import SessionState


class SessionManager:
    def __init__(self) -> None:
        self._state = SessionState.OFFLINE

    @property
    def state(self) -> SessionState:
        return self._state

    async def set_state(
        self,
        state: SessionState,
    ) -> None:
        if state == self._state:
            return

        old_state = self._state
        self._state = state

        await event_bus.publish(
            Event(
                name="session.state_changed",
                payload={
                    "old": old_state.value,
                    "new": state.value,
                },
            )
        )

    def is_state(
        self,
        state: SessionState,
    ) -> bool:
        return self._state == state