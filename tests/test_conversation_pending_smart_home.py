from __future__ import annotations

from unittest.mock import AsyncMock, Mock

import pytest

from jarvis.services.conversation_manager import ConversationManager
from jarvis.services.tool_router import ToolType
from jarvis.smart_home.device import SmartDevice
from jarvis.smart_home.service import SmartHomeService


@pytest.fixture
def devices() -> list[SmartDevice]:
    return [
        SmartDevice(
            id="plug001",
            name="Living Room Smart Plug",
            room="living room",
            device_type="cz",
            online=True,
            power=False,
        ),
        SmartDevice(
            id="plug002",
            name="Bedroom Smart Plug",
            room="bedroom",
            device_type="cz",
            online=True,
            power=False,
        ),
    ]


@pytest.fixture
def conversation(
    devices: list[SmartDevice],
) -> tuple[
    ConversationManager,
    SmartHomeService,
]:
    ai = Mock()
    ai.ask = AsyncMock(
        return_value="AI reply"
    )

    memory = Mock()
    memory.save_message = AsyncMock()
    memory.get_ai_history = AsyncMock(
        return_value=[]
    )

    router = Mock()
    router.route.return_value = (
        ToolType.SMART_HOME
    )

    smart_home = Mock(
        spec=SmartHomeService
    )

    smart_home.list_devices = AsyncMock(
        return_value=devices
    )

    smart_home.turn_on = AsyncMock(
        return_value=True
    )

    smart_home.turn_off = AsyncMock(
        return_value=True
    )

    smart_home.toggle = AsyncMock(
        return_value=True
    )

    smart_home.get_device = AsyncMock(
        return_value=None
    )

    manager = ConversationManager(
        ai=ai,
        memory=memory,
        router=router,
        smart_home=smart_home,
    )

    return manager, smart_home


@pytest.mark.asyncio
async def test_pending_turn_on_bedroom(
    conversation: tuple[
        ConversationManager,
        SmartHomeService,
    ],
) -> None:
    manager, smart_home = conversation

    first_reply = await manager.ask(
        "เปิดปลั๊ก"
    )

    assert "Living Room Smart Plug" in first_reply
    assert "Bedroom Smart Plug" in first_reply

    smart_home.turn_on.assert_not_awaited()

    second_reply = await manager.ask(
        "ห้องนอน"
    )

    smart_home.turn_on.assert_not_awaited()
    assert "ยืนยัน" in second_reply

    final_reply = await manager.ask(
        "ยืนยัน"
    )

    smart_home.turn_on.assert_awaited_once_with(
        "plug002"
    )

    assert "Bedroom Smart Plug" in final_reply


@pytest.mark.asyncio
async def test_pending_turn_off_living_room(
    conversation: tuple[
        ConversationManager,
        SmartHomeService,
    ],
) -> None:
    manager, smart_home = conversation

    first_reply = await manager.ask(
        "ปิดปลั๊ก"
    )

    assert "Living Room Smart Plug" in first_reply
    assert "Bedroom Smart Plug" in first_reply

    smart_home.turn_off.assert_not_awaited()

    second_reply = await manager.ask(
        "ห้องนั่งเล่น"
    )

    smart_home.turn_off.assert_not_awaited()
    assert "ยืนยัน" in second_reply

    final_reply = await manager.ask(
        "ยืนยัน"
    )

    smart_home.turn_off.assert_awaited_once_with(
        "plug001"
    )

    assert "Living Room Smart Plug" in final_reply


@pytest.mark.asyncio
async def test_pending_can_be_cancelled(
    conversation: tuple[
        ConversationManager,
        SmartHomeService,
    ],
) -> None:
    manager, smart_home = conversation

    await manager.ask(
        "เปิดปลั๊ก"
    )

    reply = await manager.ask(
        "ไม่เอา"
    )

    assert "ยกเลิก" in reply

    smart_home.turn_on.assert_not_awaited()
    smart_home.turn_off.assert_not_awaited()
    smart_home.toggle.assert_not_awaited()


@pytest.mark.asyncio
async def test_unknown_clarification_keeps_pending(
    conversation: tuple[
        ConversationManager,
        SmartHomeService,
    ],
) -> None:
    manager, smart_home = conversation

    await manager.ask(
        "เปิดปลั๊ก"
    )

    reply = await manager.ask(
        "ห้องครัว"
    )

    assert "Living Room Smart Plug" in reply
    assert "Bedroom Smart Plug" in reply

    smart_home.turn_on.assert_not_awaited()

    second_reply = await manager.ask(
        "ห้องนอน"
    )

    smart_home.turn_on.assert_not_awaited()
    assert "ยืนยัน" in second_reply

    await manager.ask(
        "ยืนยัน"
    )

    smart_home.turn_on.assert_awaited_once_with(
        "plug002"
    )


@pytest.mark.asyncio
async def test_pending_is_cleared_after_execution(
    conversation: tuple[
        ConversationManager,
        SmartHomeService,
    ],
) -> None:
    manager, smart_home = conversation

    await manager.ask(
        "เปิดปลั๊ก"
    )

    await manager.ask(
        "ห้องนอน"
    )

    smart_home.turn_on.assert_not_awaited()

    await manager.ask(
        "ยืนยัน"
    )

    smart_home.turn_on.assert_awaited_once_with(
        "plug002"
    )

    await manager.ask(
        "สวัสดี"
    )

    assert manager._router.route.call_count == 2


@pytest.mark.asyncio
async def test_thai_spoken_number_selects_smart_plug_2() -> None:
    ai = Mock()
    ai.ask = AsyncMock(
        return_value="AI reply"
    )

    memory = Mock()
    memory.save_message = AsyncMock()
    memory.get_ai_history = AsyncMock(
        return_value=[]
    )

    router = Mock()
    router.route.return_value = (
        ToolType.SMART_HOME
    )

    smart_home = Mock(
        spec=SmartHomeService
    )

    smart_home.list_devices = AsyncMock(
        return_value=[
            SmartDevice(
                id="plug001",
                name="Smart Plug",
                room="",
                device_type="cz",
                online=True,
                power=False,
            ),
            SmartDevice(
                id="plug002",
                name="Smart plug 2",
                room="",
                device_type="cz",
                online=True,
                power=False,
            ),
        ]
    )

    smart_home.turn_on = AsyncMock(
        return_value=True
    )

    smart_home.turn_off = AsyncMock(
        return_value=True
    )

    smart_home.toggle = AsyncMock(
        return_value=True
    )

    smart_home.get_device = AsyncMock(
        return_value=None
    )

    manager = ConversationManager(
        ai=ai,
        memory=memory,
        router=router,
        smart_home=smart_home,
    )

    first_reply = await manager.ask(
        "เปิดปลั๊ก"
    )

    assert "Smart Plug" in first_reply
    assert "Smart plug 2" in first_reply

    smart_home.turn_on.assert_not_awaited()

    second_reply = await manager.ask(
        "สมาร์ทปลั๊กสอง"
    )

    smart_home.turn_on.assert_not_awaited()
    assert "ยืนยัน" in second_reply

    final_reply = await manager.ask(
        "ยืนยัน"
    )

    smart_home.turn_on.assert_awaited_once_with(
        "plug002"
    )

    assert "Smart plug 2" in final_reply


@pytest.mark.asyncio
async def test_aggregate_smart_home_status_lists_device_states(
    conversation: tuple[
        ConversationManager,
        SmartHomeService,
    ],
) -> None:
    manager, smart_home = conversation

    reply = await manager.ask(
        "สถานะอุปกรณ์ Smart Home เป็นอย่างไร"
    )

    smart_home.list_devices.assert_awaited()

    assert "Living Room Smart Plug" in reply
    assert "Bedroom Smart Plug" in reply

    smart_home.turn_on.assert_not_awaited()
    smart_home.turn_off.assert_not_awaited()
    smart_home.toggle.assert_not_awaited()


@pytest.mark.asyncio
async def test_direct_turn_on_requires_confirmation(
    conversation: tuple[
        ConversationManager,
        SmartHomeService,
    ],
) -> None:
    manager, smart_home = conversation

    reply = await manager.ask(
        "เปิด Living Room Smart Plug"
    )

    smart_home.turn_on.assert_not_awaited()

    assert "ยืนยัน" in reply


@pytest.mark.asyncio
async def test_direct_turn_off_requires_confirmation(
    conversation: tuple[
        ConversationManager,
        SmartHomeService,
    ],
) -> None:
    manager, smart_home = conversation

    reply = await manager.ask(
        "ปิด Living Room Smart Plug"
    )

    smart_home.turn_off.assert_not_awaited()

    assert "ยืนยัน" in reply


@pytest.mark.asyncio
async def test_confirmation_executes_pending_turn_on(
    conversation: tuple[
        ConversationManager,
        SmartHomeService,
    ],
) -> None:
    manager, smart_home = conversation

    await manager.ask(
        "เปิด Living Room Smart Plug"
    )

    smart_home.turn_on.assert_not_awaited()

    reply = await manager.ask(
        "ยืนยัน"
    )

    smart_home.turn_on.assert_awaited_once_with(
        "plug001"
    )

    assert "Living Room Smart Plug" in reply


@pytest.mark.asyncio
async def test_cancelled_confirmation_does_not_execute(
    conversation: tuple[
        ConversationManager,
        SmartHomeService,
    ],
) -> None:
    manager, smart_home = conversation

    await manager.ask(
        "เปิด Living Room Smart Plug"
    )

    smart_home.turn_on.assert_not_awaited()

    reply = await manager.ask(
        "ยกเลิก"
    )

    smart_home.turn_on.assert_not_awaited()

    assert "ยกเลิก" in reply


@pytest.mark.asyncio
async def test_toggle_requires_confirmation(
    conversation: tuple[
        ConversationManager,
        SmartHomeService,
    ],
) -> None:
    manager, smart_home = conversation

    reply = await manager.ask(
        "toggle Living Room Smart Plug"
    )

    smart_home.toggle.assert_not_awaited()

    assert "ยืนยัน" in reply


@pytest.mark.asyncio
async def test_status_does_not_require_confirmation(
    conversation: tuple[
        ConversationManager,
        SmartHomeService,
    ],
) -> None:
    manager, smart_home = conversation

    reply = await manager.ask(
        "สถานะ Living Room Smart Plug"
    )

    assert "ยืนยัน" not in reply
    assert "Living Room Smart Plug" in reply

    smart_home.turn_on.assert_not_awaited()
    smart_home.turn_off.assert_not_awaited()
    smart_home.toggle.assert_not_awaited()


@pytest.mark.asyncio
async def test_ambiguous_turn_on_requires_confirmation_after_device_selection(
    conversation: tuple[
        ConversationManager,
        SmartHomeService,
    ],
) -> None:
    manager, smart_home = conversation

    first_reply = await manager.ask(
        "เปิด Smart Plug"
    )

    assert "Living Room Smart Plug" in first_reply
    assert "Bedroom Smart Plug" in first_reply

    smart_home.turn_on.assert_not_awaited()

    second_reply = await manager.ask(
        "Bedroom Smart Plug"
    )

    smart_home.turn_on.assert_not_awaited()

    assert "ยืนยัน" in second_reply

    final_reply = await manager.ask(
        "ยืนยัน"
    )

    smart_home.turn_on.assert_awaited_once_with(
        "plug002"
    )

    assert "Bedroom Smart Plug" in final_reply

@pytest.mark.asyncio
async def test_read_only_status_is_allowed_while_confirmation_is_pending(
    conversation: tuple[
        ConversationManager,
        SmartHomeService,
    ],
) -> None:
    manager, smart_home = conversation

    await manager.ask(
        "เปิด Living Room Smart Plug"
    )

    smart_home.turn_on.assert_not_awaited()

    reply = await manager.ask(
        "สถานะ Living Room Smart Plug"
    )

    assert "Living Room Smart Plug" in reply
    assert "ยืนยัน" not in reply

    smart_home.turn_on.assert_not_awaited()

    confirmation_reply = await manager.ask(
        "ยืนยัน"
    )

    smart_home.turn_on.assert_awaited_once_with(
        "plug001"
    )

    assert "Living Room Smart Plug" in confirmation_reply

@pytest.mark.asyncio
async def test_device_list_is_allowed_while_confirmation_is_pending(
    conversation: tuple[
        ConversationManager,
        SmartHomeService,
    ],
) -> None:
    manager, smart_home = conversation

    await manager.ask(
        "เปิด Living Room Smart Plug"
    )

    smart_home.turn_on.assert_not_awaited()

    reply = await manager.ask(
        "มีอุปกรณ์ Smart Home อะไรบ้าง"
    )

    assert "Living Room Smart Plug" in reply
    assert "Bedroom Smart Plug" in reply
    assert "ยืนยัน" not in reply

    smart_home.turn_on.assert_not_awaited()

    await manager.ask(
        "ยืนยัน"
    )

    smart_home.turn_on.assert_awaited_once_with(
        "plug001"
    )