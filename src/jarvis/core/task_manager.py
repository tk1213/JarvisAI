import asyncio
from collections.abc import Awaitable
from typing import Any


class TaskManager:
    def __init__(self) -> None:
        self._tasks: dict[str, asyncio.Task[Any]] = {}

    def create_task(
        self,
        name: str,
        coro: Awaitable[Any],
    ) -> None:

        self._tasks[name] = asyncio.create_task(coro)

    async def stop_all(self) -> None:

        for task in self._tasks.values():
            task.cancel()

        if self._tasks:
            await asyncio.gather(
                *self._tasks.values(),
                return_exceptions=True,
            )

        self._tasks.clear()

    def list_tasks(self) -> list[str]:
        return sorted(self._tasks.keys())


task_manager = TaskManager()