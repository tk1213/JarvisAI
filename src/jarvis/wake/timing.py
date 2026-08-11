from __future__ import annotations

import time
from dataclasses import dataclass, field


@dataclass(slots=True)
class TurnTiming:
    """Timing diagnostics for one wake-activated turn."""

    started_at: float = field(
        default_factory=time.perf_counter
    )

    wake_detected_at: float | None = None
    acknowledgement_done_at: float | None = None
    command_listen_started_at: float | None = None
    transcript_ready_at: float | None = None
    conversation_done_at: float | None = None
    tts_done_at: float | None = None

    def mark_wake_detected(self) -> None:
        self.wake_detected_at = time.perf_counter()

    def mark_acknowledgement_done(self) -> None:
        self.acknowledgement_done_at = time.perf_counter()

    def mark_command_listen_started(self) -> None:
        self.command_listen_started_at = time.perf_counter()

    def mark_transcript_ready(self) -> None:
        self.transcript_ready_at = time.perf_counter()

    def mark_conversation_done(self) -> None:
        self.conversation_done_at = time.perf_counter()

    def mark_tts_done(self) -> None:
        self.tts_done_at = time.perf_counter()

    @staticmethod
    def _duration(
        start: float | None,
        end: float | None,
    ) -> float | None:
        if start is None or end is None:
            return None

        return end - start

    @property
    def wake_seconds(self) -> float | None:
        return self._duration(
            self.started_at,
            self.wake_detected_at,
        )

    @property
    def acknowledgement_seconds(self) -> float | None:
        return self._duration(
            self.wake_detected_at,
            self.acknowledgement_done_at,
        )

    @property
    def post_ack_seconds(self) -> float | None:
        return self._duration(
            self.acknowledgement_done_at,
            self.command_listen_started_at,
        )

    @property
    def command_listen_seconds(self) -> float | None:
        return self._duration(
            self.command_listen_started_at,
            self.transcript_ready_at,
        )

    @property
    def command_capture_seconds(self) -> float | None:
        return self._duration(
            self.acknowledgement_done_at,
            self.transcript_ready_at,
        )

    @property
    def conversation_seconds(self) -> float | None:
        return self._duration(
            self.transcript_ready_at,
            self.conversation_done_at,
        )

    @property
    def tts_seconds(self) -> float | None:
        return self._duration(
            self.conversation_done_at,
            self.tts_done_at,
        )

    @property
    def total_seconds(self) -> float | None:
        return self._duration(
            self.started_at,
            self.tts_done_at,
        )