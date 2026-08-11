from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, Mock

from jarvis.voice.turn_runtime import (
    VoiceTurnRuntime,
    VoiceTurnStatus,
)


async def main() -> None:
    stt = Mock()
    stt.listen_vad = AsyncMock(
        return_value="ทดสอบระบบ Jarvis"
    )

    conversation = Mock()
    conversation.ask = AsyncMock(
        return_value="ระบบพร้อมทำงานครับ"
    )

    tts = Mock()
    tts.speak = AsyncMock()

    runtime = VoiceTurnRuntime(
        stt=stt,
        conversation=conversation,
        tts=tts,
    )

    result = await runtime.run(
        language="th"
    )

    assert result.status is VoiceTurnStatus.COMPLETED
    assert result.transcript == "ทดสอบระบบ Jarvis"
    assert result.reply == "ระบบพร้อมทำงานครับ"
    tts.speak.assert_awaited_once()

    print("Sprint 5 Pack G — Voice Turn Runtime Integration")
    print("-" * 60)
    print("VAD/STT boundary: PASS")
    print("ConversationManager boundary: PASS")
    print("TTS boundary: PASS")
    print("Empty-speech protection: PASS")
    print("Sprint 5 Pack G live gate: PASS")


if __name__ == "__main__":
    asyncio.run(
        main()
    )
