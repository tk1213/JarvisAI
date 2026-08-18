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