from __future__ import annotations

import asyncio

from jarvis.services.wake_word_service import WakeWordService
from jarvis.wake.activation import (
    WakeActivationResult,
    WakeActivationStatus,
)


class WakeActivationBoundary:
    """Stable async boundary around the hardware wake-word service."""

    def __init__(
        self,
        wake_word: WakeWordService,
    ) -> None:
        self._wake_word = wake_word
        self._active_task: asyncio.Task[float] | None = None

    @property
    def active(self) -> bool:
        return (
            self._active_task is not None
            and not self._active_task.done()
        )

    async def wait(
        self,
    ) -> WakeActivationResult:
        if self._wake_word.closed:
            return WakeActivationResult(
                status=WakeActivationStatus.CLOSED,
            )

        if self.active:
            raise RuntimeError(
                "Wake activation is already waiting."
            )

        parent_task = asyncio.current_task()

        wake_task = asyncio.create_task(
            self._wake_word.wait_for_wake_word(),
            name="jarvis-wake-wait",
        )

        self._active_task = wake_task

        try:
            score = await wake_task

            return WakeActivationResult(
                status=WakeActivationStatus.DETECTED,
                score=score,
            )

        except asyncio.CancelledError:
            parent_cancelling = (
                parent_task.cancelling()
                if parent_task is not None
                else 0
            )

            print()
            print(
                "[WAKE CANCEL DIAGNOSTIC] "
                f"parent_cancelling={parent_cancelling}, "
                f"wake_task_cancelled={wake_task.cancelled()}, "
                f"wake_service_closed={self._wake_word.closed}"
            )

            raise

        finally:
            if self._active_task is wake_task:
                self._active_task = None

    async def cancel_active_wait(
        self,
    ) -> None:
        task = self._active_task

        if task is None:
            return

        if task.done():
            self._active_task = None
            return

        task.cancel()

        try:
            await task
        except asyncio.CancelledError:
            pass
        finally:
            if self._active_task is task:
                self._active_task = None