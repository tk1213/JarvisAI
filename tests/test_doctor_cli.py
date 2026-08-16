from __future__ import annotations

from unittest.mock import AsyncMock, Mock, patch

import pytest

from jarvis.main import doctor
from jarvis.services.health_contracts import (
    HealthCheckResult,
    HealthState,
)


@pytest.mark.asyncio
async def test_doctor_returns_true_when_all_critical_checks_pass(
    capsys: pytest.CaptureFixture[str],
) -> None:
    health = Mock()
    health.operational_diagnostics = AsyncMock(
        return_value={
            "database": HealthCheckResult(
                name="database",
                state=HealthState.HEALTHY,
            ),
            "audio": HealthCheckResult(
                name="audio",
                state=HealthState.HEALTHY,
            ),
        }
    )

    app = AsyncMock()

    with (
        patch(
            "jarvis.main.JarvisApplication",
            return_value=app,
        ),
        patch(
            "jarvis.main.container.get",
            return_value=health,
        ),
    ):
        result = await doctor()

    output = capsys.readouterr().out

    assert result is True
    assert "[PASS] database" in output
    assert "[PASS] audio" in output
    assert "Overall Status: HEALTHY" in output


@pytest.mark.asyncio
async def test_doctor_returns_false_for_critical_failure(
    capsys: pytest.CaptureFixture[str],
) -> None:
    health = Mock()
    health.operational_diagnostics = AsyncMock(
        return_value={
            "database": HealthCheckResult(
                name="database",
                state=HealthState.UNAVAILABLE,
                reason="Database unavailable.",
            ),
        }
    )

    app = AsyncMock()

    with (
        patch(
            "jarvis.main.JarvisApplication",
            return_value=app,
        ),
        patch(
            "jarvis.main.container.get",
            return_value=health,
        ),
    ):
        result = await doctor()

    output = capsys.readouterr().out

    assert result is False
    assert "[FAIL] database" in output
    assert "Reason: Database unavailable." in output
    assert "Overall Status: UNHEALTHY" in output


@pytest.mark.asyncio
async def test_doctor_warns_for_noncritical_degraded_check(
    capsys: pytest.CaptureFixture[str],
) -> None:
    health = Mock()
    health.operational_diagnostics = AsyncMock(
        return_value={
            "optional_component": HealthCheckResult(
                name="optional_component",
                state=HealthState.DEGRADED,
                reason="Optional feature degraded.",
                critical=False,
            ),
        }
    )

    app = AsyncMock()

    with (
        patch(
            "jarvis.main.JarvisApplication",
            return_value=app,
        ),
        patch(
            "jarvis.main.container.get",
            return_value=health,
        ),
    ):
        result = await doctor()

    output = capsys.readouterr().out

    assert result is True
    assert "[WARN] optional_component" in output
    assert "Reason: Optional feature degraded." in output
    assert "Overall Status: HEALTHY" in output

@pytest.mark.asyncio
async def test_doctor_prints_audio_device_details(
    capsys: pytest.CaptureFixture[str],
) -> None:
    health = Mock()
    health.operational_diagnostics = AsyncMock(
        return_value={
            "audio": HealthCheckResult(
                name="audio",
                state=HealthState.HEALTHY,
                details={
                    "input": {
                        "index": 18,
                        "name": "Desktop Microphone (RØDE NT-USB Mini)",
                        "host_api": "Windows WASAPI",
                        "sample_rate": 48000,
                        "max_input_channels": 2,
                    },
                    "output": {
                        "index": 16,
                        "name": "Speakers (Realtek(R) Audio)",
                        "host_api": "Windows WASAPI",
                        "sample_rate": 48000,
                        "max_output_channels": 2,
                    },
                },
            ),
        }
    )

    app = AsyncMock()

    with (
        patch(
            "jarvis.main.JarvisApplication",
            return_value=app,
        ),
        patch(
            "jarvis.main.container.get",
            return_value=health,
        ),
    ):
        result = await doctor()

    output = capsys.readouterr().out

    assert result is True
    assert "[PASS] audio" in output
    assert "Desktop Microphone (RØDE NT-USB Mini)" in output
    assert "Windows WASAPI" in output
    assert "48000 Hz" in output
    assert "Speakers (Realtek(R) Audio)" in output

@pytest.mark.asyncio
async def test_doctor_prints_resilience_runtime_details(
    capsys: pytest.CaptureFixture[str],
) -> None:
    health = Mock()

    health.operational_diagnostics = AsyncMock(
        return_value={
            "resilience_runtime": HealthCheckResult(
                name="resilience_runtime",
                state=HealthState.DEGRADED,
                reason=(
                    "Resilience runtime reports "
                    "degraded state."
                ),
                details={
                    "summary": "resilience degraded",
                    "metrics": {
                        "plans_started": 4,
                        "plans_completed": 2,
                        "plans_failed": 2,
                        "steps_started": 8,
                        "steps_completed": 5,
                        "steps_failed": 3,
                        "retries": 2,
                        "timeouts": 1,
                        "circuit_rejections": 1,
                        "bulkhead_rejections": 0,
                        "capability_failures": {
                            "smart_home.control": 2,
                        },
                    },
                },
                critical=False,
            ),
        }
    )

    app = AsyncMock()

    with (
        patch(
            "jarvis.main.JarvisApplication",
            return_value=app,
        ),
        patch(
            "jarvis.main.container.get",
            return_value=health,
        ),
    ):
        result = await doctor()

    output = capsys.readouterr().out

    assert result is True
    assert "[WARN] resilience_runtime" in output
    assert (
        "Reason: Resilience runtime reports degraded state."
        in output
    )
    assert "Summary            : resilience degraded" in output
    assert "Plans              : 4 / 2 / 2" in output
    assert "Steps              : 8 / 5 / 3" in output
    assert "Retries            : 2" in output
    assert "Timeouts           : 1" in output
    assert "Circuit rejections : 1" in output
    assert "Bulkhead rejections: 0" in output
    assert "smart_home.control: 2" in output
    assert "Overall Status: HEALTHY" in output
