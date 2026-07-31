from pathlib import Path

from jarvis.audio.player import AudioPlayer
from jarvis.speech.tts import TextToSpeech


class TTSService:
    def __init__(
        self,
        player: AudioPlayer,
        tts: TextToSpeech,
    ) -> None:
        self.player = player
        self.tts = tts

    async def speak(
        self,
        text: str,
        output: str = "output.wav",
    ) -> Path:
        audio_file = await self.tts.generate(
            text=text,
            output=output,
        )

        self.player.play(audio_file)

        return audio_file

    async def generate_only(
        self,
        text: str,
        output: str = "output.wav",
    ) -> Path:
        return await self.tts.generate(
            text=text,
            output=output,
        )