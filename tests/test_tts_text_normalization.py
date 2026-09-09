from pathlib import Path
from unittest.mock import AsyncMock, Mock

import pytest

from jarvis.services.tts_service import TTSService


@pytest.mark.asyncio
async def test_speak_normalizes_money_before_generation(
    tmp_path: Path,
) -> None:
    audio_file = tmp_path / "reply.wav"

    player = Mock()

    def play(
        filename: Path,
        *,
        blocking: bool,
        on_playback_start,
    ) -> None:
        assert filename == audio_file
        assert blocking is False
        on_playback_start()

    player.play.side_effect = play
    player.wait.return_value = None

    tts = Mock()
    tts.generate = AsyncMock(
        return_value=audio_file
    )

    service = TTSService(
        player=player,
        tts=tts,
    )

    await service.speak(
        "ราคา 68,450 บาท",
        output=str(audio_file),
    )

    tts.generate.assert_awaited_once_with(
        text=(
            "ราคา "
            "หกหมื่นแปดพันสี่ร้อยห้าสิบบาท"
        ),
        output=str(audio_file),
    )


@pytest.mark.asyncio
async def test_generate_only_normalizes_time(
    tmp_path: Path,
) -> None:
    audio_file = tmp_path / "time.wav"

    tts = Mock()
    tts.generate = AsyncMock(
        return_value=audio_file
    )

    service = TTSService(
        player=Mock(),
        tts=tts,
    )

    result = await service.generate_only(
        "เวลา 23.30 น.",
        output=str(audio_file),
    )

    assert result == audio_file

    tts.generate.assert_awaited_once_with(
        text=(
            "เวลา ยี่สิบสามนาฬิกา "
            "สามสิบนาที"
        ),
        output=str(audio_file),
    )