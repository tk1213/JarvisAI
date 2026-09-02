from __future__ import annotations

import asyncio
from dataclasses import dataclass
from enum import StrEnum

from jarvis.wake.full_turn import (
    WakeActivatedTurnResult,
    WakeActivatedTurnRuntime,
)


class ContinuousAssistantStopReason(StrEnum):
    MAX_TURNS = "max_turns"
    STOP_REQUESTED = "stop_requested"
    CANCELLED = "cancelled"


@dataclass(slots=True, frozen=True)
class ContinuousAssistantRunResult:
    turns: tuple[WakeActivatedTurnResult, ...]
    stop_reason: ContinuousAssistantStopReason
    cancellation_stage: str | None = None

    @property
    def completed_turns(self) -> int:
        return sum(
            1
            for turn in self.turns
            if turn.completed
        )


class ContinuousAssistantRuntime:
    """Run bounded wake-activated turns with an explicit stop boundary."""

    def __init__(
        self,
        *,
        turn_runtime: WakeActivatedTurnRuntime,
    ) -> None:
        self._turn_runtime = turn_runtime
        self._stop_event = asyncio.Event()
        self._running = False

    @property
    def running(self) -> bool:
        return self._running

    def request_stop(self) -> None:
        self._stop_event.set()

    async def run(
        self,
        *,
        language: str = "th",
        max_turns: int = 3,
    ) -> ContinuousAssistantRunResult:
        if max_turns < 1:
            raise ValueError(
                "max_turns must be at least 1."
            )

        if self._running:
            raise RuntimeError(
                "ContinuousAssistantRuntime is already running."
            )

        self._running = True
        self._stop_event.clear()

        turns: list[WakeActivatedTurnResult] = []

        try:
            while len(turns) < max_turns:
                if self._stop_event.is_set():
                    return ContinuousAssistantRunResult(
                        turns=tuple(turns),
                        stop_reason=(
                            ContinuousAssistantStopReason.STOP_REQUESTED
                        ),
                    )

                try:
                    turn = await self._turn_runtime.run(
                        language=language,
                    )
                except asyncio.CancelledError:
                    current_task = asyncio.current_task()

                    if (
                        current_task is not None
                        and current_task.cancelling()
                    ):
                        raise

                    cancellation_stage = (
                        f"{self._turn_runtime.stage}:"
                        f"{self._turn_runtime.transition.stage}"
                    )

                    return ContinuousAssistantRunResult(
                        turns=tuple(turns),
                        stop_reason=(
                            ContinuousAssistantStopReason.CANCELLED
                        ),
                        cancellation_stage=cancellation_stage,
                    )

                turns.append(
                    turn
                )

            return ContinuousAssistantRunResult(
                turns=tuple(turns),
                stop_reason=(
                    ContinuousAssistantStopReason.MAX_TURNS
                ),
            )
        finally:
            self._running = False
