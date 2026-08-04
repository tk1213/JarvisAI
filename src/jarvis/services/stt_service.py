from __future__ import annotations

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
        """
        Listen using VAD by default.

        The ``seconds`` argument is kept for backward compatibility.
        Use ``listen_fixed`` when fixed-duration recording is required.
        """

        del seconds

        return await self.listen_vad(
            language=language,
        )

    async def listen_vad(
        self,
        language: str = "th",
        output: str = "record.wav",
        *,
        threshold: float = 100.0,
        vad_frame_duration_ms: int = 20,
        speech_trigger_ms: int = 60,
        silence_duration_ms: int = 900,
        pre_roll_ms: int = 300,
        max_wait_seconds: float = 10.0,
        max_record_seconds: float = 15.0,
    ) -> str:
        """
        Wait for speech and stop recording automatically
        after sustained silence.
        """

        audio_file = self.recorder.record_until_silence(
            output=output,
            threshold=threshold,
            vad_frame_duration_ms=vad_frame_duration_ms,
            speech_trigger_ms=speech_trigger_ms,
            silence_duration_ms=silence_duration_ms,
            pre_roll_ms=pre_roll_ms,
            max_wait_seconds=max_wait_seconds,
            max_record_seconds=max_record_seconds,
        )

        if audio_file is None:
            return ""

        return await self._transcribe(
            audio_file,
            language=language,
        )

    async def listen_fixed(
        self,
        seconds: float = 5.0,
        language: str = "th",
        output: str = "record.wav",
    ) -> str:
        """
        Record for a fixed duration.

        Kept as a fallback and for diagnostics.
        """

        audio_file = self.recorder.record(
            seconds=seconds,
            output=output,
        )

        return await self._transcribe(
            audio_file,
            language=language,
        )

    async def transcribe_file(
        self,
        audio_file: str | Path,
        language: str = "th",
    ) -> str:
        """
        Transcribe an existing audio file.
        """

        return await self._transcribe(
            audio_file,
            language=language,
        )

    async def _transcribe(
        self,
        audio_file: str | Path,
        *,
        language: str,
    ) -> str:
        text = await self.stt.transcribe(
            audio_file=audio_file,
            language=language,
        )

        return text.strip()