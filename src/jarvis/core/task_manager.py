from __future__ import annotations

import asyncio
from collections.abc import Awaitable
from typing import Any

from jarvis.core.logger import log


class TaskManager:
    def __init__(self) -> None:
        self._tasks: dict[str, asyncio.Task[Any]] = {}

    def create_task(
        self,
        name: str,
        coro: Awaitable[Any],
    ) -> None:
        name = name.strip()

        if not name:
            raise ValueError(
                "Task name cannot be empty."
            )

        existing_task = self._tasks.get(name)

        if (
            existing_task is not None
            and not existing_task.done()
        ):
            raise ValueError(
                f"Task '{name}' is already running."
            )

        task = asyncio.create_task(
            coro,
            name=name,
        )

        self._tasks[name] = task

        task.add_done_callback(
            lambda completed_task: self._on_task_done(
                name,
                completed_task,
            )
        )

    def _on_task_done(
        self,
        name: str,
        task: asyncio.Task[Any],
    ) -> None:
        current_task = self._tasks.get(name)

        if current_task is task:
            self._tasks.pop(
                name,
                None,
            )

        if task.cancelled():
            log.debug(
                "Background task cancelled: {}",
                name,
            )
            return

        exception = task.exception()

        if exception is not None:
            log.error(
                "Background task '{}' failed: {!r}",
                name,
                exception,
            )

    async def stop_all(self) -> None:
        tasks = list(
            self._tasks.values()
        )

        for task in tasks:
            if not task.done():
                task.cancel()

        if tasks:
            await asyncio.gather(
                *tasks,
                return_exceptions=True,
            )

        self._tasks.clear()

    def list_tasks(self) -> list[str]:
        return sorted(
            name
            for name, task in self._tasks.items()
            if not task.done()
        )

    def has_task(
        self,
        name: str,
    ) -> bool:
        task = self._tasks.get(
            name.strip()
        )

        return (
            task is not None
            and not task.done()
        )

    def __len__(self) -> int:
        return sum(
            1
            for task in self._tasks.values()
            if not task.done()
        )


task_manager = TaskManager()