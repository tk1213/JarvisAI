from __future__ import annotations

from unittest.mock import AsyncMock, Mock

import pytest

from jarvis.config import settings
from jarvis.core.event_bus import event_bus
from jarvis.services.ai_capability_resolver import AICapabilityResolver
from jarvis.services.ai_service import AIService
from jarvis.services.capability import CapabilityRequest
from jarvis.services.capability_router import CapabilityRouter
from jarvis.services.conversation_manager import ConversationManager
from jarvis.services.memory_service import MemoryService
from jarvis.services.tool_router import ToolRouter
from jarvis.skills.context import SkillContext
from jarvis.skills.loader import SkillLoader
from jarvis.skills.manager import SkillManager
from jarvis.smart_home.service import SmartHomeService


@pytest.fixture
def conversation_manager() -> ConversationManager:
    ai = Mock(spec=AIService)

    memory = Mock(spec=MemoryService)
    memory.save_message = AsyncMock()
    memory.get_ai_history = AsyncMock(
        return_value=[],
    )

    smart_home = Mock(spec=SmartHomeService)

    context = SkillContext(
        ai=ai,
        memory=memory,
        smart_home=smart_home,
        event_bus=event_bus,
        settings=settings,
    )

    skill_manager = SkillManager()

    loader = SkillLoader(
        manager=skill_manager,
        context=context,
    )

    loader.load_package(
        "jarvis.skills.builtin",
    )

    capability_router = CapabilityRouter(
        skill_manager=skill_manager,
    )

    return ConversationManager(
        ai=ai,
        memory=memory,
        router=ToolRouter(),
        smart_home=smart_home,
        capability_router=capability_router,
    )


@pytest.mark.asyncio
async def test_conversation_system_version(
    conversation_manager: ConversationManager,
) -> None:
    reply = await conversation_manager.ask(
        "system version",
    )

    assert "JarvisAI Version" in reply


@pytest.mark.asyncio
async def test_conversation_system_health(
    conversation_manager: ConversationManager,
) -> None:
    reply = await conversation_manager.ask(
        "system health",
    )

    assert "สถานะปกติ" in reply


@pytest.mark.asyncio
async def test_conversation_system_ping(
    conversation_manager: ConversationManager,
) -> None:
    reply = await conversation_manager.ask(
        "system ping",
    )

    assert "ทำงานปกติ" in reply

@pytest.mark.asyncio
async def test_ai_route_uses_capability_when_resolved(
    conversation_manager: ConversationManager,
) -> None:
    resolver = Mock(spec=AICapabilityResolver)
    resolver.resolve = AsyncMock(
        return_value=CapabilityRequest(
            capability="system.version",
        )
    )

    conversation_manager.set_capability_resolver(
        resolver,
    )

    reply = await conversation_manager.ask(
        "Jarvis ใช้เวอร์ชันอะไร",
    )

    assert "JarvisAI Version" in reply


@pytest.mark.asyncio
async def test_ai_route_falls_back_to_normal_ai(
    conversation_manager: ConversationManager,
) -> None:
    resolver = Mock(spec=AICapabilityResolver)
    resolver.resolve = AsyncMock(
        return_value=None,
    )

    conversation_manager.set_capability_resolver(
        resolver,
    )

    ai = conversation_manager._ai
    ai.ask = AsyncMock(
        return_value="Quantum computing explanation"
    )

    reply = await conversation_manager.ask(
        "Explain quantum computing",
    )

    assert reply == "Quantum computing explanation"    