from __future__ import annotations

from unittest.mock import AsyncMock, Mock

import pytest

from jarvis.services.conversation_manager import ConversationManager
from jarvis.services.tool_router import ToolType
from jarvis.smart_home.device import SmartDevice
from jarvis.smart_home.service import SmartHomeService
from jarvis.voice.dialogue_runtime import VoiceDialogueRuntime
from jarvis.voice.turn_runtime import (
    VoiceTurnResult,
    VoiceTurnRuntime,
    VoiceTurnStatus,
)


def completed(
    transcript: str,
    reply: str,
) -> VoiceTurnResult:
    return VoiceTurnResult(
        status=VoiceTurnStatus.COMPLETED,
        transcript=transcript,
        reply=reply,
    )


@pytest.mark.asyncio
async def test_dialogue_runs_one_follow_up_for_pending_smart_home() -> None:
    voice_turn = Mock()
    voice_turn.run = AsyncMock(
        side_effect=(
            completed(
                "เปิดปลั๊ก",
                "ต้องการ Smart Plug 1 หรือ Smart Plug 2 ครับ",
            ),
            completed(
                "Smart Plug 2",
                "เปิด Smart Plug 2 แล้วครับ",
            ),
        )
    )

    conversation = Mock()
    type(conversation).has_pending_smart_home = property(
        Mock(
            side_effect=(
                True,
                False,
                False,
            )
        )
    )

    runtime = VoiceDialogueRuntime(
        voice_turn=voice_turn,
        conversation=conversation,
        max_follow_ups=2,
    )

    result = await runtime.run(
        language="th"
    )

    assert len(result.turns) == 2
    assert result.follow_ups_used == 1
    assert result.pending_smart_home is False
    assert result.completed is True
    assert voice_turn.run.await_count == 2


@pytest.mark.asyncio
async def test_dialogue_does_not_follow_up_without_pending_action() -> None:
    voice_turn = Mock()
    voice_turn.run = AsyncMock(
        return_value=completed(
            "สวัสดี",
            "สวัสดีครับ",
        )
    )

    conversation = Mock()
    conversation.has_pending_smart_home = False

    runtime = VoiceDialogueRuntime(
        voice_turn=voice_turn,
        conversation=conversation,
    )

    result = await runtime.run()

    assert len(result.turns) == 1
    assert result.follow_ups_used == 0
    assert result.completed is True
    voice_turn.run.assert_awaited_once()


@pytest.mark.asyncio
async def test_dialogue_follow_up_is_bounded() -> None:
    voice_turn = Mock()
    voice_turn.run = AsyncMock(
        return_value=completed(
            "คำตอบ",
            "ยังต้องระบุอุปกรณ์ครับ",
        )
    )

    conversation = Mock()
    conversation.has_pending_smart_home = True

    runtime = VoiceDialogueRuntime(
        voice_turn=voice_turn,
        conversation=conversation,
        max_follow_ups=2,
    )

    result = await runtime.run()

    assert len(result.turns) == 3
    assert result.follow_ups_used == 2
    assert result.pending_smart_home is True
    assert result.completed is False
    assert voice_turn.run.await_count == 3


@pytest.mark.asyncio
async def test_no_speech_stops_follow_up_loop() -> None:
    voice_turn = Mock()
    voice_turn.run = AsyncMock(
        side_effect=(
            completed(
                "สถานะปลั๊ก",
                "ต้องการ Smart Plug 1 หรือ Smart Plug 2 ครับ",
            ),
            VoiceTurnResult(
                status=VoiceTurnStatus.NO_SPEECH,
                transcript="",
                reply="",
            ),
        )
    )

    conversation = Mock()
    conversation.has_pending_smart_home = True

    runtime = VoiceDialogueRuntime(
        voice_turn=voice_turn,
        conversation=conversation,
    )

    result = await runtime.run()

    assert result.follow_ups_used == 1
    assert result.turns[-1].status is VoiceTurnStatus.NO_SPEECH
    assert result.completed is False


def test_negative_follow_up_limit_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="cannot be negative",
    ):
        VoiceDialogueRuntime(
            voice_turn=Mock(),
            conversation=Mock(),
            max_follow_ups=-1,
        )

@pytest.mark.asyncio
async def test_voice_dialogue_confirms_smart_home_side_effect() -> None:
    stt = Mock()
    stt.listen_vad = AsyncMock(
        side_effect=(
            "เปิด Living Room Smart Plug",
            "ยืนยัน",
        )
    )

    tts = Mock()
    tts.speak = AsyncMock()

    memory = Mock()
    memory.save_message = AsyncMock()
    memory.save_turn = AsyncMock()
    memory.get_ai_history = AsyncMock(
        return_value=[]
    )

    router = Mock()
    router.route.return_value = ToolType.SMART_HOME

    smart_home = Mock(
        spec=SmartHomeService
    )

    device = SmartDevice(
        id="plug001",
        name="Living Room Smart Plug",
        room="living room",
        device_type="cz",
        online=True,
        power=False,
    )

    smart_home.list_devices = AsyncMock(
        return_value=[device]
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
        return_value=device
    )

    conversation = ConversationManager(
        ai=Mock(),
        memory=memory,
        router=router,
        smart_home=smart_home,
    )

    voice_turn = VoiceTurnRuntime(
        stt=stt,
        conversation=conversation,
        tts=tts,
    )

    runtime = VoiceDialogueRuntime(
        voice_turn=voice_turn,
        conversation=conversation,
        max_follow_ups=2,
    )

    result = await runtime.run(
        language="th"
    )

    smart_home.turn_on.assert_awaited_once_with(
        "plug001"
    )

    assert len(result.turns) == 2
    assert result.follow_ups_used == 1
    assert result.pending_smart_home is False
    assert result.completed is True

@pytest.mark.asyncio
async def test_voice_dialogue_cancels_smart_home_side_effect() -> None:
    stt = Mock()
    stt.listen_vad = AsyncMock(
        side_effect=(
            "เปิด Living Room Smart Plug",
            "ยกเลิก",
        )
    )

    tts = Mock()
    tts.speak = AsyncMock()

    memory = Mock()
    memory.save_message = AsyncMock()
    memory.save_turn = AsyncMock()
    memory.get_ai_history = AsyncMock(return_value=[])

    router = Mock()
    router.route.return_value = ToolType.SMART_HOME

    smart_home = Mock(spec=SmartHomeService)

    device = SmartDevice(
        id="plug001",
        name="Living Room Smart Plug",
        room="living room",
        device_type="cz",
        online=True,
        power=False,
    )

    smart_home.list_devices = AsyncMock(return_value=[device])
    smart_home.turn_on = AsyncMock(return_value=True)
    smart_home.turn_off = AsyncMock(return_value=True)
    smart_home.toggle = AsyncMock(return_value=True)
    smart_home.get_device = AsyncMock(return_value=device)

    conversation = ConversationManager(
        ai=Mock(),
        memory=memory,
        router=router,
        smart_home=smart_home,
    )

    voice_turn = VoiceTurnRuntime(
        stt=stt,
        conversation=conversation,
        tts=tts,
    )

    runtime = VoiceDialogueRuntime(
        voice_turn=voice_turn,
        conversation=conversation,
        max_follow_ups=2,
    )

    result = await runtime.run(language="th")

    smart_home.turn_on.assert_not_awaited()

    assert len(result.turns) == 2
    assert result.follow_ups_used == 1
    assert result.pending_smart_home is False
    assert result.completed is True

@pytest.mark.asyncio
async def test_voice_dialogue_allows_status_while_confirmation_is_pending() -> None:
    stt = Mock()
    stt.listen_vad = AsyncMock(
        side_effect=(
            "เปิด Living Room Smart Plug",
            "สถานะ Living Room Smart Plug",
            "ยืนยัน",
        )
    )

    tts = Mock()
    tts.speak = AsyncMock()

    memory = Mock()
    memory.save_message = AsyncMock()
    memory.save_turn = AsyncMock()
    memory.get_ai_history = AsyncMock(return_value=[])

    router = Mock()
    router.route.return_value = ToolType.SMART_HOME

    smart_home = Mock(spec=SmartHomeService)

    device = SmartDevice(
        id="plug001",
        name="Living Room Smart Plug",
        room="living room",
        device_type="cz",
        online=True,
        power=False,
    )

    smart_home.list_devices = AsyncMock(return_value=[device])
    smart_home.turn_on = AsyncMock(return_value=True)
    smart_home.turn_off = AsyncMock(return_value=True)
    smart_home.toggle = AsyncMock(return_value=True)
    smart_home.get_device = AsyncMock(return_value=device)

    conversation = ConversationManager(
        ai=Mock(),
        memory=memory,
        router=router,
        smart_home=smart_home,
    )

    voice_turn = VoiceTurnRuntime(
        stt=stt,
        conversation=conversation,
        tts=tts,
    )

    runtime = VoiceDialogueRuntime(
        voice_turn=voice_turn,
        conversation=conversation,
        max_follow_ups=2,
    )

    result = await runtime.run(language="th")

    smart_home.turn_on.assert_awaited_once_with("plug001")

    assert len(result.turns) == 3
    assert result.follow_ups_used == 2
    assert result.pending_smart_home is False
    assert result.completed is True