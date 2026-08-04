from __future__ import annotations

from unittest.mock import AsyncMock, Mock, patch

import pytest

from jarvis.core.application import JarvisApplication
from jarvis.core.container import container


@pytest.fixture(autouse=True)
def clean_container():
    container.clear()

    yield

    container.clear()


@pytest.mark.asyncio
async def test_application_remains_stopped_when_startup_fails() -> None:
    app = JarvisApplication()

    with patch(
        "jarvis.core.application.ServiceFactory.register_all",
        side_effect=RuntimeError("startup failed"),
    ), pytest.raises(
        RuntimeError,
        match="startup failed",
    ):
        await app.start(
            start_background_tasks=False,
        )

    assert app.started is False


@pytest.mark.asyncio
async def test_container_is_cleaned_when_startup_fails() -> None:
    app = JarvisApplication()

    with patch(
        "jarvis.core.application.ServiceFactory.register_all",
        side_effect=RuntimeError("startup failed"),
    ), pytest.raises(RuntimeError):
        await app.start(
            start_background_tasks=False,
        )

    assert len(container) == 0


@pytest.mark.asyncio
async def test_database_is_shutdown_when_later_startup_fails() -> None:
    app = JarvisApplication()

    database = Mock()
    database.startup = AsyncMock()
    database.shutdown = AsyncMock()

    smart_home = Mock()
    smart_home.connect = AsyncMock(
        side_effect=RuntimeError(
            "smart home startup failed"
        )
    )
    smart_home.disconnect = AsyncMock()

    system = Mock()
    system.startup = Mock()
    system.shutdown = Mock()

    original_resolve = container.resolve

    def resolve(
        name: str,
        expected_type=None,
    ):
        if name == "database":
            return database

        if name == "smart_home":
            return smart_home

        if name == "system":
            return system

        return original_resolve(
            name,
            expected_type,
        )

    with patch.object(
        container,
        "resolve",
        side_effect=resolve,
    ), pytest.raises(
        RuntimeError,
        match="smart home startup failed",
    ):
        await app.start(
            start_background_tasks=False,
        )

    database.startup.assert_awaited_once()
    database.shutdown.assert_awaited_once()

    system.startup.assert_called_once()
    system.shutdown.assert_called_once()

    assert app.started is False

@pytest.mark.asyncio
async def test_shutdown_continues_when_skill_shutdown_fails() -> None:
    app = JarvisApplication()

    skill_manager = Mock()
    skill_manager.shutdown = AsyncMock(
        side_effect=RuntimeError(
            "skill shutdown failed"
        )
    )

    smart_home = Mock()
    smart_home.disconnect = AsyncMock()

    database = Mock()
    database.shutdown = AsyncMock()

    system = Mock()
    system.shutdown = Mock()

    app.started = True
    app._skills_started = True
    app._smart_home_connected = True
    app._database_started = True
    app._system_started = True

    original_resolve = container.resolve

    def resolve(
        name: str,
        expected_type=None,
    ):
        if name == "skill_manager":
            return skill_manager

        if name == "smart_home":
            return smart_home

        if name == "database":
            return database

        if name == "system":
            return system

        return original_resolve(
            name,
            expected_type,
        )

    with patch.object(
        container,
        "resolve",
        side_effect=resolve,
    ):
        await app.shutdown()

    skill_manager.shutdown.assert_awaited_once()
    smart_home.disconnect.assert_awaited_once()
    database.shutdown.assert_awaited_once()
    system.shutdown.assert_called_once()

    assert app.started is False
    assert len(container) == 0

@pytest.mark.asyncio
async def test_shutdown_can_be_called_twice_safely() -> None:
    app = JarvisApplication()

    await app.start(
        start_background_tasks=False,
    )

    await app.shutdown()
    await app.shutdown()

    assert app.started is False
    assert len(container) == 0


@pytest.mark.asyncio
async def test_start_does_nothing_when_already_started() -> None:
    app = JarvisApplication()

    await app.start(
        start_background_tasks=False,
    )

    skill_manager = container.get(
        "skill_manager"
    )

    await app.start(
        start_background_tasks=False,
    )

    assert app.started is True
    assert (
        container.get("skill_manager")
        is skill_manager
    )

    await app.shutdown()

    assert app.started is False
    assert len(container) == 0