from __future__ import annotations

import asyncio

import pytest

from jarvis.conversation.execution_boundary import (
    ConversationExecutionBoundary,
    ConversationExecutionPolicy,
)


@pytest.mark.asyncio
async def test_boundary_returns_successful_result() -> None:
    boundary = ConversationExecutionBoundary(
        ConversationExecutionPolicy(
            timeout_seconds=1.0
        )
    )

    async def handler() -> str:
        return "ok"

    assert await boundary.run(handler) == "ok"


@pytest.mark.asyncio
async def test_boundary_converts_asyncio_timeout_to_builtin_timeout() -> None:
    boundary = ConversationExecutionBoundary(
        ConversationExecutionPolicy(
            timeout_seconds=0.01
        )
    )

    async def handler() -> str:
        await asyncio.sleep(
            1.0
        )
        return "late"

    with pytest.raises(
        TimeoutError,
        match="exceeded",
    ):
        await boundary.run(
            handler
        )


@pytest.mark.asyncio
async def test_boundary_preserves_external_cancellation() -> None:
    boundary = ConversationExecutionBoundary(
        ConversationExecutionPolicy(
            timeout_seconds=1.0
        )
    )

    started = asyncio.Event()

    async def handler() -> str:
        started.set()
        await asyncio.sleep(
            10.0
        )
        return "never"

    task = asyncio.create_task(
        boundary.run(
            handler
        )
    )

    await started.wait()
    task.cancel()

    with pytest.raises(
        asyncio.CancelledError
    ):
        await task


def test_invalid_timeout_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="greater than zero",
    ):
        ConversationExecutionPolicy(
            timeout_seconds=0
        )
