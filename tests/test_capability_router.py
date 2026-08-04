from __future__ import annotations

from unittest.mock import AsyncMock, Mock

import pytest

from jarvis.config import settings
from jarvis.core.event_bus import event_bus
from jarvis.services.ai_service import AIService
from jarvis.services.capability import CapabilityRequest
from jarvis.services.capability_registry import CapabilityRegistry
from jarvis.services.capability_router import CapabilityRouter
from jarvis.services.memory_service import MemoryService
from jarvis.skills.context import SkillContext
from jarvis.skills.loader import SkillLoader
from jarvis.skills.manager import SkillManager
from jarvis.smart_home.service import SmartHomeService


@pytest.fixture
def capability_router() -> CapabilityRouter:
    context = SkillContext(
        ai=Mock(spec=AIService),
        memory=Mock(spec=MemoryService),
        smart_home=Mock(spec=SmartHomeService),
        event_bus=event_bus,
        settings=settings,
    )

    manager = SkillManager()

    loader = SkillLoader(
        manager=manager,
        context=context,
    )

    loader.load_package(
        "jarvis.skills.builtin",
    )

    return CapabilityRouter(
        skill_manager=manager,
    )


@pytest.mark.asyncio
async def test_system_ping_capability(
    capability_router: CapabilityRouter,
) -> None:
    result = await capability_router.execute(
        "system.ping",
    )

    assert result == {
        "status": "ok",
    }


@pytest.mark.asyncio
async def test_system_health_capability(
    capability_router: CapabilityRouter,
) -> None:
    result = await capability_router.execute(
        "system.health",
    )

    assert result["healthy"] is True
    assert result["skill"] == "system"


@pytest.mark.asyncio
async def test_system_version_capability(
    capability_router: CapabilityRouter,
) -> None:
    result = await capability_router.execute(
        "system.version",
    )

    assert "jarvis" in result

@pytest.mark.asyncio
async def test_execute_capability_request(
    capability_router: CapabilityRouter,
) -> None:
    request = CapabilityRequest(
        capability="system.ping",
    )

    result = await capability_router.execute_request(
        request,
    )

    assert result == {
        "status": "ok",
    }    

@pytest.mark.asyncio
async def test_allowed_capability() -> None:
    manager = Mock(spec=SkillManager)
    manager.execute = AsyncMock(
        return_value={"status": "ok"}
    )

    registry = CapabilityRegistry(
        {"system.ping"}
    )

    router = CapabilityRouter(
        skill_manager=manager,
        registry=registry,
    )

    result = await router.execute(
        "system.ping",
    )

    assert result == {"status": "ok"}


@pytest.mark.asyncio
async def test_reject_unknown_capability() -> None:
    manager = Mock(spec=SkillManager)
    manager.execute = AsyncMock()

    registry = CapabilityRegistry(
        {"system.ping"}
    )

    router = CapabilityRouter(
        skill_manager=manager,
        registry=registry,
    )

    with pytest.raises(
        PermissionError,
        match="Capability is not allowed",
    ):
        await router.execute(
            "system.fake_command",
        )

    manager.execute.assert_not_awaited()    