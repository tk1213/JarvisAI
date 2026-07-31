from pathlib import Path

from jarvis.audio.recorder import AudioRecorder
from jarvis.speech.stt import SpeechToText


class STTService:
    def __init__(
        self,
        recorder: AudioRecorder,
        stt: SpeechToText,
    ) -> None:
        self.recorder = recorder
        self.stt = stt

    async def listen(
        self,
        seconds: float = 5.0,
        language: str = "th",
    ) -> str:
        audio_file = self.recorder.record(
            seconds=seconds,
            output="record.wav",
        )

        return await self.stt.transcribe(
            audio_file=audio_file,
            language=language,
        )

    async def transcribe_file(
        self,
        audio_file: str | Path,
        language: str = "th",
    ) -> str:
        return await self.stt.transcribe(
            audio_file=audio_file,
            language=language,
        )