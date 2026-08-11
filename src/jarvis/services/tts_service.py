from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path

from jarvis.audio.player import AudioPlayer
from jarvis.speech.tts import TextToSpeech


@dataclass(slots=True, frozen=True)
class TTSTimingDiagnostics:
    generation_seconds: float = 0.0
    player_preparation_seconds: float = 0.0
    time_to_first_audio_seconds: float = 0.0
    playback_seconds: float = 0.0
    total_seconds: float = 0.0
    cached: bool = False


class TTSService:
    def __init__(
        self,
        player: AudioPlayer,
        tts: TextToSpeech,
    ) -> None:
        self.player = player
        self.tts = tts
        self._last_timing: TTSTimingDiagnostics | None = None

    @property
    def last_timing(
        self,
    ) -> TTSTimingDiagnostics | None:
        return self._last_timing

    async def speak(
        self,
        text: str,
        output: str = "output.wav",
    ) -> Path:
        total_started = time.perf_counter()

        output_path = Path(
            output
        ).resolve()

        cached = (
            output_path.name == "wake_ack.wav"
            and output_path.exists()
        )

        if cached:
            audio_file = output_path
            generation_elapsed = 0.0

            print(
                "[Latency] TTS generation       : "
                "0.000 s (cached)"
            )

        else:
            generation_started = time.perf_counter()

            audio_file = await self.tts.generate(
                text=text,
                output=output,
            )

            generation_elapsed = (
                time.perf_counter()
                - generation_started
            )

            print(
                "[Latency] TTS generation       : "
                f"{generation_elapsed:.3f} s"
            )

        player_started = time.perf_counter()
        playback_started_at: float | None = None

        def mark_playback_start() -> None:
            nonlocal playback_started_at

            playback_started_at = time.perf_counter()

        self.player.play(
            audio_file,
            on_playback_start=mark_playback_start,
        )

        playback_finished_at = time.perf_counter()

        if playback_started_at is None:
            raise RuntimeError(
                "AudioPlayer did not report playback start."
            )

        player_prepare_elapsed = (
            playback_started_at
            - player_started
        )

        time_to_first_audio = (
            playback_started_at
            - total_started
        )

        playback_elapsed = (
            playback_finished_at
            - playback_started_at
        )

        total_elapsed = (
            playback_finished_at
            - total_started
        )

        self._last_timing = TTSTimingDiagnostics(
            generation_seconds=generation_elapsed,
            player_preparation_seconds=player_prepare_elapsed,
            time_to_first_audio_seconds=time_to_first_audio,
            playback_seconds=playback_elapsed,
            total_seconds=total_elapsed,
            cached=cached,
        )

        print(
            "[Latency] Player preparation    : "
            f"{player_prepare_elapsed:.3f} s"
        )
        print(
            "[Latency] Time to first audio   : "
            f"{time_to_first_audio:.3f} s"
        )
        print(
            "[Latency] Audio playback        : "
            f"{playback_elapsed:.3f} s"
        )
        print(
            "[Latency] TTS total             : "
            f"{total_elapsed:.3f} s"
        )

        return audio_file

    def play_existing(
        self,
        audio_file: str | Path,
    ) -> Path:
        path = Path(
            audio_file
        ).resolve()

        self.player.play(
            path
        )

        return path

    async def generate_only(
        self,
        text: str,
        output: str = "output.wav",
    ) -> Path:
        return await self.tts.generate(
            text=text,
            output=output,
        )