from __future__ import annotations

import asyncio
from dataclasses import dataclass
from enum import StrEnum

from jarvis.services.tts_service import TTSService
from jarvis.services.voice_service import VoiceService
from jarvis.wake.boundary import WakeActivationBoundary
from jarvis.wake.timing import TurnTiming


class WakeCommandTransitionStage(StrEnum):
    IDLE = "idle"
    WAKE_WAIT = "wake_wait"
    ACKNOWLEDGEMENT = "acknowledgement"
    POST_ACK_SETTLE = "post_ack_settle"
    COMMAND_LISTEN = "command_listen"
    COMPLETED = "completed"


@dataclass(slots=True, frozen=True)
class WakeCommandTransitionResult:
    wake_score: float
    transcript: str
    timing: TurnTiming | None = None

    @property
    def completed(self) -> bool:
        return bool(
            self.transcript.strip()
        )


class WakeCommandTransition:
    """One wake -> acknowledge -> settle -> command-listen transition."""

    def __init__(
        self,
        *,
        wake: WakeActivationBoundary,
        voice: VoiceService,
        tts: TTSService,
        acknowledgement: str = "ครับ คุณ TK",
        post_ack_settle_seconds: float = 0.25,
    ) -> None:
        if post_ack_settle_seconds < 0:
            raise ValueError(
                "post_ack_settle_seconds cannot be negative."
            )

        self._wake = wake
        self._voice = voice
        self._tts = tts
        self._acknowledgement = acknowledgement
        self._post_ack_settle_seconds = post_ack_settle_seconds
        self._stage = WakeCommandTransitionStage.IDLE

    @property
    def stage(self) -> WakeCommandTransitionStage:
        return self._stage

    async def run(
        self,
        *,
        language: str = "th",
    ) -> WakeCommandTransitionResult:
        timing = TurnTiming()

        self._stage = WakeCommandTransitionStage.WAKE_WAIT
        activation = await self._wake.wait()

        if not activation.detected:
            raise RuntimeError(
                "Wake activation did not complete."
            )

        if activation.score is None:
            raise RuntimeError(
                "Detected wake activation has no score."
            )
        timing.mark_wake_detected()

        self._stage = WakeCommandTransitionStage.ACKNOWLEDGEMENT

        await self._tts.speak(
            text=self._acknowledgement,
            output="wake_ack.wav",
        )

        timing.mark_acknowledgement_done()

        if self._post_ack_settle_seconds > 0:
            self._stage = WakeCommandTransitionStage.POST_ACK_SETTLE

            await asyncio.sleep(
                self._post_ack_settle_seconds
            )

        self._stage = WakeCommandTransitionStage.COMMAND_LISTEN

        timing.mark_command_listen_started()

        transcript = (
            await self._voice.listen_for_text(
                language=language,
            )
        ).strip()
        timing.mark_transcript_ready()


        self._stage = WakeCommandTransitionStage.COMPLETED

        return WakeCommandTransitionResult(
            wake_score=activation.score,
            transcript=transcript,
            timing=timing,
        )
