from __future__ import annotations

from dataclasses import dataclass

from jarvis.config import Settings
from jarvis.core.event_bus import EventBus
from jarvis.services.ai_service import AIService
from jarvis.services.memory_service import MemoryService
from jarvis.smart_home.service import SmartHomeService


@dataclass(slots=True)
class SkillContext:
    ai: AIService
    memory: MemoryService
    smart_home: SmartHomeService
    event_bus: EventBus
    settings: Settings