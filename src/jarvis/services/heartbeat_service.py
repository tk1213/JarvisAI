import asyncio

from jarvis.core.logger import log


class HeartbeatService:

    async def run(self) -> None:

        while True:

            log.info("Heartbeat")

            await asyncio.sleep(5)