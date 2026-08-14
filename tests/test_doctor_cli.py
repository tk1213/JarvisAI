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
