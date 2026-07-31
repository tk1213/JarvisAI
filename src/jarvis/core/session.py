from __future__ import annotations

from enum import Enum


class SessionState(str, Enum):
    OFFLINE = "offline"
    STARTING = "starting"
    IDLE = "idle"
    LISTENING = "listening"
    THINKING = "thinking"
    SPEAKING = "speaking"
    SHUTTING_DOWN = "shutting_down"