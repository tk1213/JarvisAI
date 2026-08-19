from __future__ import annotations

import asyncio

import pytest

from jarvis.core.task_manager import TaskManager


@pytest.mark.asyncio
async def test_create_and_complete_task() -> None:
    manager = TaskManager()

    async def worker() -> None:
        await asyncio.sleep(0)

    manager.create_task(
        "worker",
        worker(),
    )

    assert manager.has_task("worker")
    assert "worker" in manager.list_tasks()

    await asyncio.sleep(0)
    await asyncio.sleep(0)

    assert not manager.has_task("worker")
    assert "worker" not in manager.list_tasks()
    assert len(manager) == 0


@pytest.mark.asyncio
async def test_stop_all_cancels_tasks() -> None:
    manager = TaskManager()

    started = asyncio.Event()

    async def worker() -> None:
        started.set()

        while True:
            await asyncio.sleep(1)

    manager.create_task(
        "worker",
        worker(),
    )

    await started.wait()

    assert manager.has_task("worker")

    await manager.stop_all()

    assert not manager.has_task("worker")
    assert manager.list_tasks() == []
    assert len(manager) == 0


@pytest.mark.asyncio
async def test_duplicate_running_task_is_rejected() -> None:
    manager = TaskManager()

    started = asyncio.Event()

    async def worker() -> None:
        started.set()

        while True:
            await asyncio.sleep(1)

    manager.create_task(
        "worker",
        worker(),
    )

    await started.wait()

    duplicate = worker()

    try:
        with pytest.raises(
            ValueError,
            match="already running",
        ):
            manager.create_task(
                "worker",
                duplicate,
            )
    finally:
        duplicate.close()
        await manager.stop_all()


def test_empty_task_name_is_rejected() -> None:
    manager = TaskManager()

    async def worker() -> None:
        pass

    coroutine = worker()

    try:
        with pytest.raises(
            ValueError,
            match="Task name cannot be empty",
        ):
            manager.create_task(
                "   ",
                coroutine,
            )
    finally:
        coroutine.close()

@pytest.mark.asyncio
async def test_stop_all_waits_for_task_cancellation_cleanup() -> None:
    manager = TaskManager()

    started = asyncio.Event()
    cleanup_complete = asyncio.Event()

    async def worker() -> None:
        started.set()

        try:
            await asyncio.Future()
        finally:
            await asyncio.sleep(0)
            cleanup_complete.set()

    manager.create_task(
        "worker",
        worker(),
    )

    await started.wait()

    await manager.stop_all()

    assert cleanup_complete.is_set()
    assert manager.list_tasks() == []
    assert len(manager) == 0


@pytest.mark.asyncio
async def test_stop_all_is_safe_when_called_twice() -> None:
    manager = TaskManager()

    started = asyncio.Event()

    async def worker() -> None:
        started.set()
        await asyncio.Future()

    manager.create_task(
        "worker",
        worker(),
    )

    await started.wait()

    await manager.stop_all()
    await manager.stop_all()

    assert manager.list_tasks() == []
    assert len(manager) == 0