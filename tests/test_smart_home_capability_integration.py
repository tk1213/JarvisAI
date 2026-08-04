from __future__ import annotations

from unittest.mock import Mock

import pytest

from jarvis.config import settings
from jarvis.core.event_bus import EventBus
from jarvis.services.ai_service import AIService
from jarvis.services.capability import CapabilityRequest
from jarvis.services.capability_registry import CapabilityRegistry
from jarvis.services.capability_router import CapabilityRouter
from jarvis.services.memory_service import MemoryService
from jarvis.skills.context import SkillContext
from jarvis.skills.loader import SkillLoader
from jarvis.skills.manager import SkillManager
from jarvis.smart_home.mock_adapter import MockAdapter
from jarvis.smart_home.service import SmartHomeService


@pytest.fixture
def integration_services() -> tuple[
    SmartHomeService,
    CapabilityRouter,
]:
    smart_home = SmartHomeService(
        adapter=MockAdapter(),
    )

    context = SkillContext(
        ai=Mock(spec=AIService),
        memory=Mock(spec=MemoryService),
        smart_home=smart_home,
        event_bus=EventBus(),
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

    registry = CapabilityRegistry.from_capabilities(
        manager.list_capability_definitions(),
    )

    router = CapabilityRouter(
        skill_manager=manager,
        registry=registry,
    )

    return smart_home, router


@pytest.mark.asyncio
async def test_turn_on_by_thai_device_query(
    integration_services: tuple[
        SmartHomeService,
        CapabilityRouter,
    ],
) -> None:
    smart_home, router = integration_services

    result = await router.execute_request(
        CapabilityRequest(
            capability="smart_home.turn_on",
            arguments={
                "device_query": "ไฟห้องนั่งเล่น",
            },
        )
    )

    assert result["success"] is True
    assert result["device_id"] == "light001"
    assert result["device_name"] == "Living Room Light"
    assert result["power"] is True

    device = await smart_home.get_device(
        "light001",
    )

    assert device is not None
    assert device.power is True


@pytest.mark.asyncio
async def test_turn_off_by_english_device_query(
    integration_services: tuple[
        SmartHomeService,
        CapabilityRouter,
    ],
) -> None:
    smart_home, router = integration_services

    await smart_home.turn_on(
        "light002",
    )

    result = await router.execute_request(
        CapabilityRequest(
            capability="smart_home.turn_off",
            arguments={
                "device_query": "bedroom light",
            },
        )
    )

    assert result["success"] is True
    assert result["device_id"] == "light002"
    assert result["power"] is False

    device = await smart_home.get_device(
        "light002",
    )

    assert device is not None
    assert device.power is False


@pytest.mark.asyncio
async def test_toggle_by_device_query(
    integration_services: tuple[
        SmartHomeService,
        CapabilityRouter,
    ],
) -> None:
    smart_home, router = integration_services

    result = await router.execute_request(
        CapabilityRequest(
            capability="smart_home.toggle",
            arguments={
                "device_query": "พัดลมห้องนั่งเล่น",
            },
        )
    )

    assert result["success"] is True
    assert result["device_id"] == "fan001"
    assert result["power"] is True

    device = await smart_home.get_device(
        "fan001",
    )

    assert device is not None
    assert device.power is True


@pytest.mark.asyncio
async def test_status_by_device_query(
    integration_services: tuple[
        SmartHomeService,
        CapabilityRouter,
    ],
) -> None:
    smart_home, router = integration_services

    await smart_home.turn_on(
        "ac001",
    )

    result = await router.execute_request(
        CapabilityRequest(
            capability="smart_home.status",
            arguments={
                "device_query": "แอร์ห้องนอน",
            },
        )
    )

    assert result["success"] is True

    device = result["device"]

    assert device["id"] == "ac001"
    assert device["name"] == "Bedroom Air Conditioner"
    assert device["power"] is True
    assert device["online"] is True


@pytest.mark.asyncio
async def test_unknown_device_query_is_safe(
    integration_services: tuple[
        SmartHomeService,
        CapabilityRouter,
    ],
) -> None:
    _, router = integration_services

    result = await router.execute_request(
        CapabilityRequest(
            capability="smart_home.turn_on",
            arguments={
                "device_query": "เครื่องชงกาแฟ",
            },
        )
    )

    assert result == {
        "success": False,
        "error": "device_not_found",
        "device_query": "เครื่องชงกาแฟ",
    }


@pytest.mark.asyncio
async def test_legacy_device_id_still_supported(
    integration_services: tuple[
        SmartHomeService,
        CapabilityRouter,
    ],
) -> None:
    smart_home, router = integration_services

    result = await router.execute_request(
        CapabilityRequest(
            capability="smart_home.turn_on",
            arguments={
                "device_id": "garage001",
            },
        )
    )

    assert result["success"] is True
    assert result["device_id"] == "garage001"

    device = await smart_home.get_device(
        "garage001",
    )

    assert device is not None
    assert device.power is True


@pytest.mark.asyncio
async def test_unregistered_capability_is_blocked(
    integration_services: tuple[
        SmartHomeService,
        CapabilityRouter,
    ],
) -> None:
    _, router = integration_services

    with pytest.raises(
        PermissionError,
        match="Capability is not allowed",
    ):
        await router.execute_request(
            CapabilityRequest(
                capability="smart_home.delete_device",
                arguments={
                    "device_query": "ไฟห้องนั่งเล่น",
                },
            )
        )