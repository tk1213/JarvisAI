from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, Mock

import pytest

from jarvis.database.db import DatabaseManager


class FakeSessionContext:
    def __init__(
        self,
        session: Mock,
    ) -> None:
        self._session = session

    async def __aenter__(
        self,
    ) -> Mock:
        return self._session

    async def __aexit__(
        self,
        exc_type: object,
        exc_value: object,
        traceback: object,
    ) -> None:
        del exc_type
        del exc_value
        del traceback


@pytest.mark.asyncio
async def test_session_commits_on_success() -> None:
    manager = DatabaseManager()

    session = Mock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()

    manager.session_factory = Mock(
        return_value=FakeSessionContext(
            session
        )
    )

    async with manager.session():
        pass

    session.commit.assert_awaited_once()
    session.rollback.assert_not_awaited()


@pytest.mark.asyncio
async def test_session_rolls_back_on_exception() -> None:
    manager = DatabaseManager()

    session = Mock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()

    manager.session_factory = Mock(
        return_value=FakeSessionContext(
            session
        )
    )

    with pytest.raises(
        RuntimeError,
        match="transaction failed",
    ):
        async with manager.session():
            raise RuntimeError(
                "transaction failed"
            )

    session.commit.assert_not_awaited()
    session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_session_rolls_back_on_external_cancellation() -> None:
    manager = DatabaseManager()

    entered = asyncio.Event()

    session = Mock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()

    manager.session_factory = Mock(
        return_value=FakeSessionContext(
            session
        )
    )

    async def transaction() -> None:
        async with manager.session():
            entered.set()
            await asyncio.Future()

    task = asyncio.create_task(
        transaction()
    )

    await entered.wait()

    task.cancel()

    with pytest.raises(
        asyncio.CancelledError,
    ):
        await task

    session.commit.assert_not_awaited()
    session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_session_rolls_back_when_commit_is_cancelled() -> None:
    manager = DatabaseManager()

    commit_started = asyncio.Event()

    session = Mock()
    session.rollback = AsyncMock()

    async def blocked_commit() -> None:
        commit_started.set()
        await asyncio.Future()

    session.commit = AsyncMock(
        side_effect=blocked_commit,
    )

    manager.session_factory = Mock(
        return_value=FakeSessionContext(
            session
        )
    )

    async def transaction() -> None:
        async with manager.session():
            pass

    task = asyncio.create_task(
        transaction()
    )

    await commit_started.wait()

    task.cancel()

    with pytest.raises(
        asyncio.CancelledError,
    ):
        await task

    session.commit.assert_awaited_once()
    session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_shutdown_disposes_engine_and_clears_started_state() -> None:
    manager = DatabaseManager()

    engine = Mock()
    engine.dispose = AsyncMock()

    manager.engine = engine
    manager.started = True

    await manager.shutdown()

    engine.dispose.assert_awaited_once()
    assert manager.started is False


@pytest.mark.asyncio
async def test_shutdown_failure_preserves_started_state() -> None:
    manager = DatabaseManager()

    engine = Mock()
    engine.dispose = AsyncMock(
        side_effect=RuntimeError(
            "dispose failed"
        )
    )

    manager.engine = engine
    manager.started = True

    with pytest.raises(
        RuntimeError,
        match="dispose failed",
    ):
        await manager.shutdown()

    assert manager.started is True

@pytest.mark.asyncio
async def test_cancelled_startup_remains_retryable() -> None:
    manager = DatabaseManager()

    first_startup_entered = asyncio.Event()
    allow_retry = asyncio.Event()
    execute_calls = 0

    connection = Mock()

    async def execute(*args, **kwargs) -> None:
        nonlocal execute_calls
        del args
        del kwargs

        execute_calls += 1

        if execute_calls == 1:
            first_startup_entered.set()
            await asyncio.Future()

        await allow_retry.wait()

    connection.execute = AsyncMock(
        side_effect=execute,
    )
    connection.run_sync = AsyncMock()

    context = AsyncMock()
    context.__aenter__.return_value = connection
    context.__aexit__.return_value = None

    engine = Mock()
    engine.begin.return_value = context

    manager.engine = engine
    manager.create_memory_tables = AsyncMock()
    manager.create_agent_memory_tables = AsyncMock()

    first_task = asyncio.create_task(
        manager.startup()
    )

    await first_startup_entered.wait()

    first_task.cancel()

    with pytest.raises(
        asyncio.CancelledError,
    ):
        await first_task

    assert manager.started is False
    assert execute_calls == 1

    retry_task = asyncio.create_task(
        manager.startup()
    )

    while execute_calls < 2:
        await asyncio.sleep(0)

    assert retry_task.done() is False
    assert manager.started is False

    allow_retry.set()

    await retry_task

    assert manager.started is True
    assert execute_calls == 2
    assert engine.begin.call_count == 2

@pytest.mark.asyncio
async def test_shutdown_cancellation_preserves_started_state() -> None:
    manager = DatabaseManager()

    dispose_started = asyncio.Event()

    async def blocked_dispose() -> None:
        dispose_started.set()
        await asyncio.Future()

    engine = Mock()
    engine.dispose = AsyncMock(
        side_effect=blocked_dispose,
    )

    manager.engine = engine
    manager.started = True

    task = asyncio.create_task(
        manager.shutdown()
    )

    await dispose_started.wait()

    task.cancel()

    with pytest.raises(
        asyncio.CancelledError,
    ):
        await task

    engine.dispose.assert_awaited_once()
    assert manager.started is True