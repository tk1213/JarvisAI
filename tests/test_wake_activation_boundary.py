from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, Mock

import pytest

from jarvis.wake.activation import WakeActivationStatus
from jarvis.wake.boundary import WakeActivationBoundary


@pytest.mark.asyncio
async def test_boundary_returns_detected_score() -> None:
    wake_word = Mock()
    wake_word.closed = False
    wake_word.wait_for_wake_word = AsyncMock(
        return_value=0.87
    )

    result = await WakeActivationBoundary(
        wake_word
    ).wait()

    assert result.status is WakeActivationStatus.DETECTED
    assert result.score == pytest.approx(
        0.87
    )
    wake_word.wait_for_wake_word.assert_awaited_once_with()


@pytest.mark.asyncio
async def test_boundary_does_not_wait_when_service_closed() -> None:
    wake_word = Mock()
    wake_word.closed = True
    wake_word.wait_for_wake_word = AsyncMock()

    result = await WakeActivationBoundary(
        wake_word
    ).wait()

    assert result.status is WakeActivationStatus.CLOSED
    assert result.score is None
    wake_word.wait_for_wake_word.assert_not_awaited()
@pytest.mark.asyncio
async def test_cancel_active_wait_cancels_wake_task_and_clears_state() -> None:
    started = asyncio.Event()

    async def wait_for_wake_word() -> float:
        started.set()
        await asyncio.Future()
        return 0.0

    wake_word = Mock()
    wake_word.closed = False
    wake_word.wait_for_wake_word = AsyncMock(
        side_effect=wait_for_wake_word
    )

    boundary = WakeActivationBoundary(
        wake_word
    )

    wait_task = asyncio.create_task(
        boundary.wait()
    )

    await started.wait()

    assert boundary.active is True

    await boundary.cancel_active_wait()

    assert boundary.active is False

    with pytest.raises(
        asyncio.CancelledError
    ):
        await wait_task

@pytest.mark.asyncio
async def test_boundary_can_wait_again_after_active_wait_is_cancelled() -> None:
    first_started = asyncio.Event()
    calls = 0

    async def wait_for_wake_word() -> float:
        nonlocal calls
        calls += 1

        if calls == 1:
            first_started.set()
            await asyncio.Future()

        return 0.91

    wake_word = Mock()
    wake_word.closed = False
    wake_word.wait_for_wake_word = AsyncMock(
        side_effect=wait_for_wake_word
    )

    boundary = WakeActivationBoundary(
        wake_word
    )

    first_wait = asyncio.create_task(
        boundary.wait()
    )

    await first_started.wait()
    await boundary.cancel_active_wait()

    with pytest.raises(
        asyncio.CancelledError
    ):
        await first_wait

    result = await boundary.wait()

    assert result.status is WakeActivationStatus.DETECTED
    assert result.score == pytest.approx(
        0.91
    )
    assert boundary.active is False

@pytest.mark.asyncio
async def test_parent_cancellation_propagates_and_clears_active_state() -> None:
    started = asyncio.Event()

    async def wait_for_wake_word() -> float:
        started.set()
        await asyncio.Future()
        return 0.0

    wake_word = Mock()
    wake_word.closed = False
    wake_word.wait_for_wake_word = AsyncMock(
        side_effect=wait_for_wake_word
    )

    boundary = WakeActivationBoundary(
        wake_word
    )

    wait_task = asyncio.create_task(
        boundary.wait()
    )

    await started.wait()

    assert boundary.active is True

    wait_task.cancel()

    with pytest.raises(
        asyncio.CancelledError
    ):
        await wait_task

    assert boundary.active is False

@pytest.mark.asyncio
async def test_concurrent_wait_is_rejected() -> None:
    started = asyncio.Event()

    async def wait_for_wake_word() -> float:
        started.set()
        await asyncio.Future()
        return 0.0

    wake_word = Mock()
    wake_word.closed = False
    wake_word.wait_for_wake_word = AsyncMock(
        side_effect=wait_for_wake_word
    )

    boundary = WakeActivationBoundary(
        wake_word
    )

    first_wait = asyncio.create_task(
        boundary.wait()
    )

    await started.wait()

    with pytest.raises(
        RuntimeError,
        match="Wake activation is already waiting",
    ):
        await boundary.wait()

    await boundary.cancel_active_wait()

    with pytest.raises(
        asyncio.CancelledError
    ):
        await first_wait

@pytest.mark.asyncio
async def test_cancelling_boundary_does_not_close_wake_service() -> None:
    started = asyncio.Event()

    async def wait_for_wake_word() -> float:
        started.set()
        await asyncio.Future()
        return 0.0

    wake_word = Mock()
    wake_word.closed = False
    wake_word.wait_for_wake_word = AsyncMock(
        side_effect=wait_for_wake_word
    )
    wake_word.close = Mock()

    boundary = WakeActivationBoundary(
        wake_word
    )

    wait_task = asyncio.create_task(
        boundary.wait()
    )

    await started.wait()
    await boundary.cancel_active_wait()

    with pytest.raises(
        asyncio.CancelledError
    ):
        await wait_task

    wake_word.close.assert_not_called()
    assert boundary.active is False

@pytest.mark.asyncio
async def test_parent_cancellation_does_not_write_raw_console_diagnostic(
    capsys: pytest.CaptureFixture[str],
) -> None:
    started = asyncio.Event()

    async def wait_for_wake_word() -> float:
        started.set()
        await asyncio.Future()
        return 0.0

    wake_word = Mock()
    wake_word.closed = False
    wake_word.wait_for_wake_word = AsyncMock(
        side_effect=wait_for_wake_word
    )

    boundary = WakeActivationBoundary(
        wake_word
    )

    wait_task = asyncio.create_task(
        boundary.wait()
    )

    await started.wait()

    wait_task.cancel()

    with pytest.raises(
        asyncio.CancelledError
    ):
        await wait_task

    output = capsys.readouterr().out

    assert "[WAKE CANCEL DIAGNOSTIC]" not in output
    assert boundary.active is False

@pytest.mark.asyncio
async def test_cancel_active_wait_caller_cancellation_preserves_wake_cleanup() -> None:
    started = asyncio.Event()
    cleanup_started = asyncio.Event()
    allow_cleanup = asyncio.Event()
    cleanup_finished = asyncio.Event()

    async def wait_for_wake_word() -> float:
        started.set()

        try:
            await asyncio.Future()

        finally:
            cleanup_started.set()
            await allow_cleanup.wait()
            cleanup_finished.set()

        return 0.0

    wake_word = Mock()
    wake_word.closed = False
    wake_word.wait_for_wake_word = AsyncMock(
        side_effect=wait_for_wake_word
    )

    boundary = WakeActivationBoundary(
        wake_word
    )

    wait_task = asyncio.create_task(
        boundary.wait()
    )

    await started.wait()

    cancel_task = asyncio.create_task(
        boundary.cancel_active_wait()
    )

    await cleanup_started.wait()

    cancel_task.cancel()

    await asyncio.sleep(0)

    assert cleanup_finished.is_set() is False

    allow_cleanup.set()

    with pytest.raises(
        asyncio.CancelledError
    ):
        await cancel_task

    assert cleanup_finished.is_set() is True
    assert boundary.active is False

    with pytest.raises(
        asyncio.CancelledError
    ):
        await wait_task

@pytest.mark.asyncio
async def test_wait_caller_cancellation_preserves_wake_cleanup() -> None:
    started = asyncio.Event()
    cleanup_started = asyncio.Event()
    allow_cleanup = asyncio.Event()
    cleanup_finished = asyncio.Event()

    async def wait_for_wake_word() -> float:
        started.set()

        try:
            await asyncio.Future()

        finally:
            cleanup_started.set()
            await allow_cleanup.wait()
            cleanup_finished.set()

        return 0.0

    wake_word = Mock()
    wake_word.closed = False
    wake_word.wait_for_wake_word = AsyncMock(
        side_effect=wait_for_wake_word
    )

    boundary = WakeActivationBoundary(
        wake_word
    )

    wait_task = asyncio.create_task(
        boundary.wait()
    )

    await started.wait()

    wait_task.cancel()

    await cleanup_started.wait()
    await asyncio.sleep(0)

    assert cleanup_finished.is_set() is False

    allow_cleanup.set()

    with pytest.raises(
        asyncio.CancelledError
    ):
        await wait_task

    assert cleanup_finished.is_set() is True
    assert boundary.active is False