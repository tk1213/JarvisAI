from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from jarvis.smart_home.device import SmartDevice


class SmartHomeAction(str, Enum):
    TURN_ON = "turn_on"
    TURN_OFF = "turn_off"
    TOGGLE = "toggle"
    STATUS = "status"


@dataclass(
    slots=True,
    frozen=True,
)
class PendingSmartHomeAction:
    action: SmartHomeAction
    candidates: tuple[SmartDevice, ...]

    def __post_init__(self) -> None:
        if len(self.candidates) < 2:
            raise ValueError(
                "Pending smart home action requires "
                "at least two candidate devices."
            )


class PendingSmartHomeActionStore:
    def __init__(self) -> None:
        self._pending: PendingSmartHomeAction | None = None

    @property
    def pending(self) -> PendingSmartHomeAction | None:
        return self._pending

    @property
    def has_pending(self) -> bool:
        return self._pending is not None

    def set(
        self,
        pending: PendingSmartHomeAction,
    ) -> None:
        self._pending = pending

    def clear(self) -> None:
        self._pending = None

    def consume(self) -> PendingSmartHomeAction | None:
        pending = self._pending
        self._pending = None

        return pending