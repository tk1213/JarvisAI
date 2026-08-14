from __future__ import annotations

import asyncio

from jarvis.core.logger import log


class HeartbeatService:
    def __init__(
        self,
        interval: float = 5.0,
    ) -> None:
        if interval <= 0:
            raise ValueError("Heartbeat interval must be greater than zero.")

        self._interval = float(interval)
        self._running = False

    @property
    def interval(self) -> float:
        return self._interval

    @property
    def running(self) -> bool:
        return self._running

    async def run(self) -> None:
        self._running = True

        try:
            while True:
                log.info("Heartbeat")

                await asyncio.sleep(self._interval)
        finally:
            self._running = False
