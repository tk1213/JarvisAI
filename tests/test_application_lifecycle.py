from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, Mock, patch

import pytest

from jarvis.core.application import JarvisApplication
from jarvis.core.container import container
from jarvis.core.service_factory import ServiceFactory


@pytest.fixture(autouse=True)
def clean_container():
    container.clear()

    yield

    container.clear()



@asynccontextmanager
async def empty_database_session():
    session = AsyncMock()

    list_result = Mock()
    list_mappings = Mock()
    list_mappings.all.return_value = []
    list_result.mappings.return_value = list_mappings

    count_result = Mock()
    count_mappings = Mock()
    count_mappings.first.return_value = {
        "total": 0,
    }
    count_result.mappings.return_value = count_mappings

    async def execute(
        statement,
        parameters=None,
    ):
        del parameters

        sql = str(
            statement
        ).upper()

        if "COUNT(*)" in sql:
            return count_result

        return list_result

    session.execute = AsyncMock(
        side_effect=execute
    )

    yield session


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
    database.session = empty_database_session

    smart_home = Mock()
    smart_home.connect = AsyncMock()
    smart_home.disconnect = AsyncMock()

    system = Mock()
    system.startup = Mock()
    system.shutdown = Mock()

    commands = Mock()
    commands.register_default_commands = Mock(
        side_effect=RuntimeError(
            "command registration failed"
        )
    )

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

        if name == "commands":
            return commands

        return original_resolve(
            name,
            expected_type,
        )

    with (
        patch.object(
            container,
            "resolve",
            side_effect=resolve,
        ),
        pytest.raises(
            RuntimeError,
            match="command registration failed",
        ),
    ):
        await app.start(
            start_background_tasks=False,
        )

        await asyncio.sleep(0)

    database.startup.assert_awaited_once()
    database.shutdown.assert_awaited_once()

    smart_home.connect.assert_awaited_once()
    smart_home.disconnect.assert_awaited_once()

    system.startup.assert_called_once()
    system.shutdown.assert_called_once()

    commands.register_default_commands.assert_called_once()

    assert app.started is False
    assert len(container) == 0

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

@pytest.mark.asyncio
async def test_database_startup_failure_remains_fatal() -> None:
    app = JarvisApplication()

    database = Mock()
    database.startup = AsyncMock(
        side_effect=RuntimeError(
            "database startup failed"
        )
    )
    database.shutdown = AsyncMock()

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

        if name == "system":
            return system

        return original_resolve(
            name,
            expected_type,
        )

    with (
        patch.object(
            container,
            "resolve",
            side_effect=resolve,
        ),
        pytest.raises(
            RuntimeError,
            match="database startup failed",
        ),
    ):
        await app.start(
            start_background_tasks=False,
        )

    system.startup.assert_called_once()
    system.shutdown.assert_called_once()

    database.startup.assert_awaited_once()
    database.shutdown.assert_not_awaited()

    assert app.started is False
    assert len(container) == 0


@pytest.mark.asyncio
async def test_smart_home_connection_failure_is_degraded_not_fatal() -> None:
    app = JarvisApplication()

    smart_home = Mock()
    smart_home.connect = AsyncMock(
        side_effect=RuntimeError(
            "smart home unavailable"
        )
    )
    smart_home.disconnect = AsyncMock()

    original_resolve = container.resolve

    def resolve(
        name: str,
        expected_type=None,
    ):
        if name == "smart_home":
            return smart_home

        return original_resolve(
            name,
            expected_type,
        )

    with patch.object(
        container,
        "resolve",
        side_effect=resolve,
    ):
        await app.start(
            start_background_tasks=False,
        )

        assert app.started is True
        assert app._smart_home_connected is False

        await app.shutdown()

    smart_home.connect.assert_awaited_once()
    smart_home.disconnect.assert_not_awaited()

    assert app.started is False
    assert len(container) == 0

@pytest.mark.asyncio
async def test_smart_home_startup_failure_is_visible_as_degraded() -> None:
    app = JarvisApplication()

    await app.start(
        start_background_tasks=False,
    )

    try:
        smart_home = container.get(
            "smart_home"
        )
        health = container.get(
            "health"
        )

        assert smart_home.connected is True

        smart_home._connected = False

        results = await health.runtime_readiness()

        result = results["smart_home"]

        assert result.state.value == "degraded"
        assert result.passed is False
        assert result.available is True
        assert result.critical is False
        assert result.reason == (
            "Smart Home service is available but not connected."
        )

    finally:
            await app.shutdown()

@pytest.mark.asyncio
async def test_smart_home_connect_failure_starts_application_degraded() -> None:
    app = JarvisApplication()

    original_resolve = container.resolve

    smart_home = Mock()
    smart_home.connect = AsyncMock(
        side_effect=RuntimeError(
            "smart home unavailable"
        )
    )
    smart_home.disconnect = AsyncMock()
    smart_home.connected = False

    def resolve(
        name: str,
        expected_type=None,
    ):
        if name == "smart_home":
            return smart_home

        return original_resolve(
            name,
            expected_type,
        )

    with patch.object(
        container,
        "resolve",
        side_effect=resolve,
    ):
        await app.start(
            start_background_tasks=False,
        )

        assert app.started is True
        assert app._smart_home_connected is False

        health = container.get(
            "health"
        )

        results = await health.runtime_readiness()
        result = results["smart_home"]

        assert result.state.value == "degraded"
        assert result.critical is False
        assert result.reason == (
            "Smart Home service is available but not connected."
        )

        await app.shutdown()

    smart_home.connect.assert_awaited_once()
    smart_home.disconnect.assert_not_awaited()

@pytest.mark.asyncio
async def test_voice_registration_failure_is_degraded_not_fatal() -> None:
    app = JarvisApplication()

    original_register_voice = ServiceFactory.register_voice

    def fail_voice_registration(
        self: ServiceFactory,
    ) -> None:
        raise RuntimeError(
            "audio subsystem unavailable"
        )

    with patch.object(
        ServiceFactory,
        "register_voice",
        fail_voice_registration,
    ):
        await app.start(
            start_background_tasks=True,
        )

        await asyncio.sleep(0)

    try:
        assert app.started is True

        assert container.has(
            "system"
        )
        assert container.has(
            "database"
        )
        assert container.has(
            "ai"
        )
        assert container.has(
            "conversation"
        )

        assert not container.has(
            "audio"
        )
        assert not container.has(
            "stt"
        )
        assert not container.has(
            "tts"
        )
        assert not container.has(
            "wake_word"
        )
        assert not container.has(
            "assistant_runtime"
        )

    finally:
        await app.shutdown()

    ServiceFactory.register_voice = (
        original_register_voice
    )

@pytest.mark.asyncio
async def test_voice_registration_failure_is_operationally_degraded(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app = JarvisApplication()

    def fail_voice_registration(
        self: ServiceFactory,
    ) -> None:
        raise RuntimeError(
            "voice runtime unavailable"
        )

    with patch.object(
        ServiceFactory,
        "register_voice",
        fail_voice_registration,
    ):
        await app.start(
            start_background_tasks=False,
        )

    try:
        assert app.started is True

        heartbeat = container.get(
            "heartbeat"
        )
        heartbeat._running = True

        monkeypatch.setattr(
            "jarvis.services.health_service.task_manager.list_tasks",
            lambda: ["heartbeat"],
        )

        health = container.get(
            "health"
        )

        results = await health.runtime_readiness()

        for name in (
            "audio",
            "stt",
            "tts",
            "wake_word",
            "assistant_runtime",
        ):
            result = results[name]

            assert result.state.value == "degraded"
            assert result.passed is False
            assert result.available is True
            assert result.critical is False

        assert (
            await health.is_operationally_ready()
            is True
        )

    finally:
        await app.shutdown()

@pytest.mark.asyncio
async def test_ai_registration_failure_remains_fatal() -> None:
    app = JarvisApplication()

    with (
        patch.object(
            ServiceFactory,
            "register_ai",
            side_effect=RuntimeError(
                "AI subsystem unavailable"
            ),
        ),
        pytest.raises(
            RuntimeError,
            match="AI subsystem unavailable",
        ),
    ):
        await app.start(
            start_background_tasks=False,
        )

    assert app.started is False
    assert len(container) == 0

@pytest.mark.asyncio
async def test_application_uses_skill_runtime_without_legacy_plugins() -> None:
    app = JarvisApplication()

    await app.start(
        start_background_tasks=False,
    )

    try:
        skill_manager = container.get(
            "skill_manager"
        )

        assert "smart_home" in (
            skill_manager.list_started_skills()
        )
        assert "system" in (
            skill_manager.list_started_skills()
        )

    finally:
        await app.shutdown()

@pytest.mark.asyncio
async def test_shutdown_finishes_remaining_cleanup_before_propagating_cancellation() -> None:
    app = JarvisApplication()

    skill_manager = Mock()
    skill_manager.shutdown = AsyncMock(
        side_effect=asyncio.CancelledError()
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

    with (
        patch.object(
            container,
            "resolve",
            side_effect=resolve,
        ),
        pytest.raises(
            asyncio.CancelledError
        ),
    ):
        await app.shutdown()

    skill_manager.shutdown.assert_awaited_once()
    smart_home.disconnect.assert_awaited_once()
    database.shutdown.assert_awaited_once()
    system.shutdown.assert_called_once()

    assert app.started is False
    assert len(container) == 0

@pytest.mark.asyncio
async def test_shutdown_preserves_cancellation_when_later_cleanup_fails() -> None:
    app = JarvisApplication()

    skill_manager = Mock()
    skill_manager.shutdown = AsyncMock(
        side_effect=asyncio.CancelledError()
    )

    smart_home = Mock()
    smart_home.disconnect = AsyncMock(
        side_effect=RuntimeError(
            "smart home shutdown failed"
        )
    )

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

    with (
        patch.object(
            container,
            "resolve",
            side_effect=resolve,
        ),
        pytest.raises(
            asyncio.CancelledError
        ),
    ):
        await app.shutdown()

    skill_manager.shutdown.assert_awaited_once()
    smart_home.disconnect.assert_awaited_once()
    database.shutdown.assert_awaited_once()
    system.shutdown.assert_called_once()

    assert app.started is False
    assert len(container) == 0

@pytest.mark.asyncio
async def test_startup_rollback_finishes_remaining_cleanup_before_propagating_cancellation() -> None:
    app = JarvisApplication()

    skill_manager = Mock()
    skill_manager.shutdown = AsyncMock(
        side_effect=asyncio.CancelledError()
    )

    smart_home = Mock()
    smart_home.disconnect = AsyncMock()

    database = Mock()
    database.shutdown = AsyncMock()

    system = Mock()
    system.shutdown = Mock()

    app._skills_started = True
    app._smart_home_connected = True
    app._database_started = True
    app._system_started = True

    def resolve(
        name: str,
        expected_type: object,
    ) -> object:
        del expected_type

        services = {
            "skill_manager": skill_manager,
            "smart_home": smart_home,
            "database": database,
            "system": system,
        }

        return services[name]

    with (
        patch.object(
            container,
            "resolve",
            side_effect=resolve,
        ),
        pytest.raises(
            asyncio.CancelledError
        ),
    ):
        await app._rollback_startup()

    skill_manager.shutdown.assert_awaited_once()
    smart_home.disconnect.assert_awaited_once()
    database.shutdown.assert_awaited_once()
    system.shutdown.assert_called_once()

    assert app._skills_started is False
    assert app._smart_home_connected is False
    assert app._database_started is False
    assert app._system_started is False
    assert app.started is False
    assert len(container) == 0

@pytest.mark.asyncio
async def test_startup_rollback_preserves_cancellation_when_later_cleanup_fails() -> None:
    app = JarvisApplication()

    skill_manager = Mock()
    skill_manager.shutdown = AsyncMock(
        side_effect=asyncio.CancelledError()
    )

    smart_home = Mock()
    smart_home.disconnect = AsyncMock(
        side_effect=RuntimeError(
            "smart home rollback failed"
        )
    )

    database = Mock()
    database.shutdown = AsyncMock()

    system = Mock()
    system.shutdown = Mock()

    app._skills_started = True
    app._smart_home_connected = True
    app._database_started = True
    app._system_started = True

    def resolve(
        name: str,
        expected_type: object,
    ) -> object:
        del expected_type

        services = {
            "skill_manager": skill_manager,
            "smart_home": smart_home,
            "database": database,
            "system": system,
        }

        return services[name]

    with (
        patch.object(
            container,
            "resolve",
            side_effect=resolve,
        ),
        pytest.raises(
            asyncio.CancelledError
        ),
    ):
        await app._rollback_startup()

    skill_manager.shutdown.assert_awaited_once()
    smart_home.disconnect.assert_awaited_once()
    database.shutdown.assert_awaited_once()
    system.shutdown.assert_called_once()

    assert app._skills_started is False
    assert app._smart_home_connected is False
    assert app._database_started is False
    assert app._system_started is False
    assert app.started is False
    assert len(container) == 0

@pytest.mark.asyncio
async def test_startup_propagates_rollback_cancellation() -> None:
    app = JarvisApplication()

    app._rollback_startup = AsyncMock(  # type: ignore[method-assign]
        side_effect=asyncio.CancelledError()
    )

    with (
        patch(
            "jarvis.core.application.ServiceFactory.register_all",
            side_effect=RuntimeError(
                "startup failed"
            ),
        ),
        pytest.raises(
            asyncio.CancelledError
        ),
    ):
        await app.start(
            start_background_tasks=False,
        )

    app._rollback_startup.assert_awaited_once()
    assert app.started is False