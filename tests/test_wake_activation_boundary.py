from __future__ import annotations

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
