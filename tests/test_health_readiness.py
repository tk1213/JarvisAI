from __future__ import annotations

import pytest

from jarvis.core.container import container
from jarvis.services.health_contracts import HealthState
from jarvis.services.health_service import HealthService


class ConnectedSmartHome:
    connected = True


class DisconnectedSmartHome:
    connected = False


@pytest.mark.asyncio
async def test_openai_readiness_is_healthy_with_credentials(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "jarvis.services.health_service.settings.openai_api_key",
        "test-key",
    )

    service = HealthService()
    results = await service.readiness()

    result = results["openai_configuration"]

    assert result.state is HealthState.HEALTHY
    assert result.passed is True
    assert result.reason is None


@pytest.mark.asyncio
async def test_openai_readiness_is_unavailable_without_credentials(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "jarvis.services.health_service.settings.openai_api_key",
        None,
    )

    service = HealthService()
    results = await service.readiness()

    result = results["openai_configuration"]

    assert result.state is HealthState.UNAVAILABLE
    assert result.passed is False
    assert result.reason == "OpenAI API credentials are missing."


@pytest.mark.asyncio
async def test_mock_smart_home_configuration_is_ready(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "jarvis.services.health_service.settings.smart_home_provider",
        "mock",
    )

    service = HealthService()
    results = await service.readiness()

    result = results["smart_home_configuration"]

    assert result.state is HealthState.HEALTHY
    assert result.passed is True
    assert result.details["provider"] == "mock"


@pytest.mark.asyncio
async def test_tuya_configuration_is_ready_with_credentials(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "jarvis.services.health_service.settings.smart_home_provider",
        "tuya",
    )
    monkeypatch.setattr(
        "jarvis.services.health_service.settings.tuya_access_id",
        "access-id",
    )
    monkeypatch.setattr(
        "jarvis.services.health_service.settings.tuya_access_key",
        "access-key",
    )

    service = HealthService()
    results = await service.readiness()

    result = results["smart_home_configuration"]

    assert result.state is HealthState.HEALTHY
    assert result.passed is True
    assert result.details["provider"] == "tuya"


@pytest.mark.asyncio
async def test_tuya_configuration_is_unavailable_without_credentials(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "jarvis.services.health_service.settings.smart_home_provider",
        "tuya",
    )
    monkeypatch.setattr(
        "jarvis.services.health_service.settings.tuya_access_id",
        None,
    )
    monkeypatch.setattr(
        "jarvis.services.health_service.settings.tuya_access_key",
        None,
    )

    service = HealthService()
    results = await service.readiness()

    result = results["smart_home_configuration"]

    assert result.state is HealthState.UNAVAILABLE
    assert result.passed is False
    assert result.reason == "Tuya credentials are missing."


@pytest.mark.asyncio
async def test_unsupported_smart_home_provider_is_unavailable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "jarvis.services.health_service.settings.smart_home_provider",
        "unsupported",
    )

    service = HealthService()
    results = await service.readiness()

    result = results["smart_home_configuration"]

    assert result.state is HealthState.UNAVAILABLE
    assert result.passed is False
    assert result.reason == (
        "Unsupported smart-home provider: unsupported"
    )


@pytest.mark.asyncio
async def test_runtime_services_are_ready_when_registered() -> None:
    existing = dict(
        container._services  # type: ignore[attr-defined]
    )

    try:
        container.clear()

        for name in (
            "audio",
            "stt",
            "tts",
            "wake_word",
            "assistant_runtime",
            "smart_home_adapter",
        ):
            container.register(
                name,
                object(),
            )

        container.register(
            "smart_home",
            ConnectedSmartHome(),
        )

        service = HealthService()
        results = await service.runtime_readiness()

        assert results["audio"].passed is True
        assert results["stt"].passed is True
        assert results["tts"].passed is True
        assert results["wake_word"].passed is True
        assert results["assistant_runtime"].passed is True
        assert results["smart_home"].passed is True
        assert results["smart_home_adapter"].passed is True

    finally:
        container.clear()

        for name, registered_service in existing.items():
            container.register(
                name,
                registered_service,
            )


@pytest.mark.asyncio
async def test_runtime_services_report_missing_components() -> None:
    existing = dict(
        container._services  # type: ignore[attr-defined]
    )

    try:
        container.clear()

        service = HealthService()
        results = await service.runtime_readiness()

        expected_names = {
            "audio",
            "stt",
            "tts",
            "wake_word",
            "assistant_runtime",
            "smart_home",
            "smart_home_adapter",
        }

        assert set(results) == expected_names

        for name in (
            "audio",
            "stt",
            "tts",
            "wake_word",
            "assistant_runtime",
        ):
            result = results[name]

            assert result.state is HealthState.DEGRADED
            assert result.passed is False
            assert result.available is True
            assert result.critical is False
            assert result.reason == (
                "Voice runtime component is unavailable: "
                f"{name}"
            )

        for name in (
            "smart_home",
            "smart_home_adapter",
        ):
            result = results[name]

            assert result.state is HealthState.UNAVAILABLE
            assert result.passed is False
            assert result.available is False
            assert result.critical is True
            assert result.reason == (
                f"Runtime service is unavailable: {name}"
            )

    finally:
        container.clear()

        for name, registered_service in existing.items():
            container.register(
                name,
                registered_service,
            )


@pytest.mark.asyncio
async def test_full_readiness_combines_configuration_and_runtime(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    existing = dict(
        container._services  # type: ignore[attr-defined]
    )

    try:
        container.clear()

        monkeypatch.setattr(
            "jarvis.services.health_service.settings.openai_api_key",
            "test-key",
        )
        monkeypatch.setattr(
            "jarvis.services.health_service.settings.smart_home_provider",
            "mock",
        )

        for name in (
            "audio",
            "stt",
            "tts",
            "wake_word",
            "assistant_runtime",
            "smart_home_adapter",
        ):
            container.register(
                name,
                object(),
            )

        container.register(
            "smart_home",
            ConnectedSmartHome(),
        )

        service = HealthService()
        results = await service.full_readiness()

        assert results["openai_configuration"].passed is True
        assert results["smart_home_configuration"].passed is True
        assert results["audio"].passed is True
        assert results["stt"].passed is True
        assert results["tts"].passed is True
        assert results["wake_word"].passed is True
        assert results["assistant_runtime"].passed is True
        assert results["smart_home"].passed is True
        assert results["smart_home_adapter"].passed is True

    finally:
        container.clear()

        for name, registered_service in existing.items():
            container.register(
                name,
                registered_service,
            )


@pytest.mark.asyncio
async def test_full_readiness_preserves_failure_details(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    existing = dict(
        container._services  # type: ignore[attr-defined]
    )

    try:
        container.clear()

        monkeypatch.setattr(
            "jarvis.services.health_service.settings.openai_api_key",
            None,
        )
        monkeypatch.setattr(
            "jarvis.services.health_service.settings.smart_home_provider",
            "tuya",
        )
        monkeypatch.setattr(
            "jarvis.services.health_service.settings.tuya_access_id",
            None,
        )
        monkeypatch.setattr(
            "jarvis.services.health_service.settings.tuya_access_key",
            None,
        )

        service = HealthService()
        results = await service.full_readiness()

        assert (
            results["openai_configuration"].reason
            == "OpenAI API credentials are missing."
        )
        assert (
            results["smart_home_configuration"].reason
            == "Tuya credentials are missing."
        )
        assert results["audio"].passed is False
        assert results["assistant_runtime"].passed is False

    finally:
        container.clear()

        for name, registered_service in existing.items():
            container.register(
                name,
                registered_service,
            )


@pytest.mark.asyncio
async def test_operational_diagnostics_combines_health_and_readiness(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    existing = dict(
        container._services  # type: ignore[attr-defined]
    )

    class Database:
        async def health_check(
            self,
        ) -> bool:
            return True

    class RunningHeartbeat:
        running = True

    try:
        container.clear()

        monkeypatch.setattr(
            "jarvis.services.health_service.settings.openai_api_key",
            "test-key",
        )
        monkeypatch.setattr(
            "jarvis.services.health_service.settings.smart_home_provider",
            "mock",
        )
        monkeypatch.setattr(
            "jarvis.services.health_service.task_manager.list_tasks",
            lambda: ["heartbeat"],
        )

        container.register(
            "system",
            object(),
        )
        container.register(
            "commands",
            object(),
        )
        container.register(
            "database",
            Database(),
        )
        container.register(
            "heartbeat",
            RunningHeartbeat(),
        )

        for name in (
            "audio",
            "stt",
            "tts",
            "wake_word",
            "assistant_runtime",
            "smart_home_adapter",
        ):
            container.register(
                name,
                object(),
            )

        container.register(
            "smart_home",
            ConnectedSmartHome(),
        )

        service = HealthService()
        results = await service.operational_diagnostics()

        assert "service_container" in results
        assert "database" in results
        assert "heartbeat_task" in results
        assert "openai_configuration" in results
        assert "smart_home_configuration" in results
        assert "audio" in results
        assert "stt" in results
        assert "tts" in results
        assert "wake_word" in results
        assert "assistant_runtime" in results

    finally:
        container.clear()

        for name, registered_service in existing.items():
            container.register(
                name,
                registered_service,
            )


@pytest.mark.asyncio
async def test_operational_ready_requires_all_critical_checks(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    existing = dict(
        container._services  # type: ignore[attr-defined]
    )

    try:
        container.clear()

        monkeypatch.setattr(
            "jarvis.services.health_service.settings.openai_api_key",
            None,
        )
        monkeypatch.setattr(
            "jarvis.services.health_service.settings.smart_home_provider",
            "mock",
        )
        monkeypatch.setattr(
            "jarvis.services.health_service.task_manager.list_tasks",
            list,
        )

        service = HealthService()

        assert (
            await service.is_operationally_ready()
            is False
        )

    finally:
        container.clear()

        for name, registered_service in existing.items():
            container.register(
                name,
                registered_service,
            )


@pytest.mark.asyncio
async def test_smart_home_runtime_is_degraded_when_disconnected() -> None:
    existing = dict(
        container._services  # type: ignore[attr-defined]
    )

    try:
        container.clear()

        container.register(
            "smart_home",
            DisconnectedSmartHome(),
        )
        container.register(
            "smart_home_adapter",
            object(),
        )

        service = HealthService()
        results = await service.runtime_readiness()

        smart_home = results["smart_home"]

        assert smart_home.state is HealthState.DEGRADED
        assert smart_home.passed is False
        assert smart_home.available is True
        assert smart_home.critical is False
        assert smart_home.reason == (
            "Smart Home service is available but not connected."
        )

        assert results["smart_home_adapter"].passed is True

    finally:
        container.clear()

        for name, registered_service in existing.items():
            container.register(
                name,
                registered_service,
            )


@pytest.mark.asyncio
async def test_smart_home_runtime_is_healthy_when_connected() -> None:
    existing = dict(
        container._services  # type: ignore[attr-defined]
    )

    try:
        container.clear()

        container.register(
            "smart_home",
            ConnectedSmartHome(),
        )
        container.register(
            "smart_home_adapter",
            object(),
        )

        service = HealthService()
        results = await service.runtime_readiness()

        smart_home = results["smart_home"]

        assert smart_home.state is HealthState.HEALTHY
        assert smart_home.passed is True
        assert smart_home.reason is None

    finally:
        container.clear()

        for name, registered_service in existing.items():
            container.register(
                name,
                registered_service,
            )

@pytest.mark.asyncio
async def test_missing_voice_runtime_is_noncritical_degraded() -> None:
    existing = dict(
        container._services  # type: ignore[attr-defined]
    )

    try:
        container.clear()

        service = HealthService()
        results = await service.runtime_readiness()

        for name in (
            "audio",
            "stt",
            "tts",
            "wake_word",
            "assistant_runtime",
        ):
            result = results[name]

            assert result.state is HealthState.DEGRADED
            assert result.passed is False
            assert result.available is True
            assert result.critical is False
            assert result.reason == (
                f"Voice runtime component is unavailable: {name}"
            )

    finally:
        container.clear()

        for name, registered_service in existing.items():
            container.register(
                name,
                registered_service,
            )

@pytest.mark.asyncio
async def test_missing_voice_runtime_does_not_fail_operational_readiness(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    existing = dict(
        container._services  # type: ignore[attr-defined]
    )

    class Database:
        async def health_check(
            self,
        ) -> bool:
            return True

    class RunningHeartbeat:
        running = True

    try:
        container.clear()

        monkeypatch.setattr(
            "jarvis.services.health_service.settings.openai_api_key",
            "test-key",
        )
        monkeypatch.setattr(
            "jarvis.services.health_service.settings.smart_home_provider",
            "mock",
        )
        monkeypatch.setattr(
            "jarvis.services.health_service.task_manager.list_tasks",
            lambda: ["heartbeat"],
        )

        container.register(
            "system",
            object(),
        )
        container.register(
            "commands",
            object(),
        )
        container.register(
            "database",
            Database(),
        )
        container.register(
            "heartbeat",
            RunningHeartbeat(),
        )
        container.register(
            "resilience_runtime",
            object(),
        )
        container.register(
            "smart_home",
            ConnectedSmartHome(),
        )
        container.register(
            "smart_home_adapter",
            object(),
        )

        service = HealthService()

        assert await service.is_operationally_ready() is True

    finally:
        container.clear()

        for name, registered_service in existing.items():
            container.register(
                name,
                registered_service,
            )