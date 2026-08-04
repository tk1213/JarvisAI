from __future__ import annotations

from unittest.mock import AsyncMock, Mock

import pytest

from jarvis.services.ai_service import AIService
from jarvis.services.conversation_manager import ConversationManager
from jarvis.services.memory_service import MemoryService
from jarvis.services.tool_router import ToolRouter, ToolType
from jarvis.smart_home.device import SmartDevice
from jarvis.smart_home.service import SmartHomeService


@pytest.fixture
def conversation() -> tuple[
    ConversationManager,
    SmartHomeService,
]:
    ai = Mock(
        spec=AIService,
    )

    memory = Mock(
        spec=MemoryService,
    )

    memory.save_message = AsyncMock()

    memory.get_ai_history = AsyncMock(
        return_value=[],
    )

    router = Mock(
        spec=ToolRouter,
    )

    router.route.return_value = (
        ToolType.SMART_HOME
    )

    smart_home = Mock(
        spec=SmartHomeService,
    )

    smart_home.list_devices = AsyncMock(
        return_value=[
            SmartDevice(
                id="plug001",
                name="Living Room Smart Plug",
                room="Living Room",
                device_type="cz",
                online=True,
                power=False,
            ),
            SmartDevice(
                id="plug002",
                name="Bedroom Smart Plug",
                room="Bedroom",
                device_type="cz",
                online=True,
                power=False,
            ),
        ]
    )

    smart_home.turn_on = AsyncMock(
        return_value=True,
    )

    smart_home.turn_off = AsyncMock(
        return_value=True,
    )

    smart_home.toggle = AsyncMock(
        return_value=True,
    )

    smart_home.get_device = AsyncMock(
        return_value=None,
    )

    manager = ConversationManager(
        ai=ai,
        memory=memory,
        router=router,
        smart_home=smart_home,
    )

    return manager, smart_home


@pytest.mark.asyncio
async def test_ambiguous_device_does_not_turn_on(
    conversation: tuple[
        ConversationManager,
        SmartHomeService,
    ],
) -> None:
    manager, smart_home = conversation

    reply = await manager.ask(
        "เปิดปลั๊ก",
    )

    assert (
        "Living Room Smart Plug"
        in reply
    )

    assert (
        "Bedroom Smart Plug"
        in reply
    )

    smart_home.turn_on.assert_not_awaited()


@pytest.mark.asyncio
async def test_ambiguous_device_does_not_turn_off(
    conversation: tuple[
        ConversationManager,
        SmartHomeService,
    ],
) -> None:
    manager, smart_home = conversation

    reply = await manager.ask(
        "ปิดปลั๊ก",
    )

    assert (
        "Living Room Smart Plug"
        in reply
    )

    assert (
        "Bedroom Smart Plug"
        in reply
    )

    smart_home.turn_off.assert_not_awaited()


@pytest.mark.asyncio
async def test_exact_device_name_is_allowed(
    conversation: tuple[
        ConversationManager,
        SmartHomeService,
    ],
) -> None:
    manager, smart_home = conversation

    reply = await manager.ask(
        "เปิด Bedroom Smart Plug",
    )

    assert (
        reply
        == "เปิด Bedroom Smart Plug แล้วครับ"
    )

    smart_home.turn_on.assert_awaited_once_with(
        "plug002"
    )


@pytest.mark.asyncio
async def test_ambiguous_reply_is_saved_to_memory(
    conversation: tuple[
        ConversationManager,
        SmartHomeService,
    ],
) -> None:
    manager, _ = conversation

    memory = manager._memory

    reply = await manager.ask(
        "เปิดปลั๊ก",
    )

    assert (
        "Living Room Smart Plug"
        in reply
    )

    assert (
        "Bedroom Smart Plug"
        in reply
    )

    assert memory.save_message.await_count == 2