from __future__ import annotations

from unittest.mock import Mock

import pytest

from jarvis.config import settings
from jarvis.core.event_bus import event_bus
from jarvis.services.ai_service import AIService
from jarvis.services.memory_service import MemoryService
from jarvis.skills.context import SkillContext
from jarvis.smart_home.mock_adapter import MockAdapter
from jarvis.smart_home.service import SmartHomeService


@pytest.fixture
def sample_text() -> str:
    return "Hello Jarvis"


@pytest.fixture
def sample_command() -> str:
    return "Turn on the living room light"


@pytest.fixture
def skill_context() -> SkillContext:
    smart_home = SmartHomeService(
        adapter=MockAdapter(),
    )

    return SkillContext(
        ai=Mock(spec=AIService),
        memory=Mock(spec=MemoryService),
        smart_home=smart_home,
        event_bus=event_bus,
        settings=settings,
    )