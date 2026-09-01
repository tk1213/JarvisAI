from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, Mock

import pytest

from jarvis.main import _shutdown_application


@pytest.mark.asyncio
async def test_shutdown_application_completes_cleanup_when_caller_is_cancelled() -> None:
    cleanup_started = asyncio.Event()
    cleanup_release = asyncio.Event()

    app = Mock()

    async def shutdown() -> None:
        cleanup_started.set()
        await cleanup_release.wait()

    app.shutdown = AsyncMock(
        side_effect=shutdown
    )

    task = asyncio.create_task(
        _shutdown_application(app)
    )

    await cleanup_started.wait()

    task.cancel()

    await asyncio.sleep(0)

    assert task.done() is False

    cleanup_release.set()

    await task

    app.shutdown.assert_awaited_once()

@pytest.mark.asyncio
async def test_shutdown_application_propagates_cleanup_cancellation() -> None:
    app = Mock()

    app.shutdown = AsyncMock(
        side_effect=asyncio.CancelledError()
    )

    with pytest.raises(
        asyncio.CancelledError
    ):
        await _shutdown_application(app)

    app.shutdown.assert_awaited_once()