from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from jarvis.services.heartbeat_service import (
    HeartbeatService,
)


def test_heartbeat_uses_default_interval() -> None:
    service = HeartbeatService()

    assert service.interval == 5.0
    assert service.running is False


def test_heartbeat_accepts_custom_interval() -> None:
    service = HeartbeatService(
        interval=1.5,
    )

    assert service.interval == 1.5


def test_heartbeat_rejects_non_positive_interval() -> None:
    with pytest.raises(
        ValueError,
        match="Heartbeat interval must be greater than zero.",
    ):
        HeartbeatService(
            interval=0,
        )


@pytest.mark.asyncio
async def test_heartbeat_reports_running_state() -> None:
    service = HeartbeatService(
        interval=1.0,
    )

    entered_sleep = asyncio.Event()
    release_sleep = asyncio.Event()

    async def controlled_sleep(
        seconds: float,
    ) -> None:
        assert seconds == 1.0
        entered_sleep.set()
        await release_sleep.wait()

    with patch(
        "jarvis.services.heartbeat_service.asyncio.sleep",
        side_effect=controlled_sleep,
    ):
        task = asyncio.create_task(service.run())

        await entered_sleep.wait()

        assert service.running is True

        release_sleep.set()
        task.cancel()

        with pytest.raises(asyncio.CancelledError):
            await task

    assert service.running is False


@pytest.mark.asyncio
async def test_heartbeat_propagates_cancellation() -> None:
    service = HeartbeatService()

    sleep = AsyncMock(side_effect=asyncio.CancelledError())

    with (
        patch(
            "jarvis.services.heartbeat_service.asyncio.sleep",
            new=sleep,
        ),
        pytest.raises(asyncio.CancelledError),
    ):
        await service.run()

    assert service.running is False
    sleep.assert_awaited_once_with(5.0)

@pytest.mark.asyncio
async def test_heartbeat_can_restart_after_cancellation() -> None:
    service = HeartbeatService(
        interval=1.0,
    )

    first_sleep_started = asyncio.Event()
    second_sleep_started = asyncio.Event()
    sleep_calls = 0

    async def controlled_sleep(
        seconds: float,
    ) -> None:
        nonlocal sleep_calls

        assert seconds == 1.0

        sleep_calls += 1

        if sleep_calls == 1:
            first_sleep_started.set()
        elif sleep_calls == 2:
            second_sleep_started.set()

        await asyncio.Event().wait()

    with patch(
        "jarvis.services.heartbeat_service.asyncio.sleep",
        side_effect=controlled_sleep,
    ):
        first_task = asyncio.create_task(
            service.run()
        )

        await first_sleep_started.wait()

        assert service.running is True

        first_task.cancel()

        with pytest.raises(
            asyncio.CancelledError,
        ):
            await first_task

        assert service.running is False

        second_task = asyncio.create_task(
            service.run()
        )

        await second_sleep_started.wait()

        assert service.running is True

        second_task.cancel()

        with pytest.raises(
            asyncio.CancelledError,
        ):
            await second_task

    assert service.running is False
    assert sleep_calls == 2