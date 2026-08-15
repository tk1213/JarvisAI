from __future__ import annotations

from unittest.mock import AsyncMock, Mock

import pytest

from jarvis.smart_home.service import SmartHomeService


def test_smart_home_service_starts_disconnected() -> None:
    adapter = Mock()

    service = SmartHomeService(
        adapter=adapter,
    )

    assert service.connected is False


@pytest.mark.asyncio
async def test_smart_home_service_marks_connected_after_connect() -> None:
    adapter = Mock()
    adapter.connect = AsyncMock()

    service = SmartHomeService(
        adapter=adapter,
    )

    await service.connect()

    assert service.connected is True
    adapter.connect.assert_awaited_once()


@pytest.mark.asyncio
async def test_smart_home_service_remains_disconnected_when_connect_fails() -> None:
    adapter = Mock()
    adapter.connect = AsyncMock(
        side_effect=RuntimeError(
            "connection failed"
        )
    )

    service = SmartHomeService(
        adapter=adapter,
    )

    with pytest.raises(
        RuntimeError,
        match="connection failed",
    ):
        await service.connect()

    assert service.connected is False


@pytest.mark.asyncio
async def test_smart_home_service_marks_disconnected_after_disconnect() -> None:
    adapter = Mock()
    adapter.connect = AsyncMock()
    adapter.disconnect = AsyncMock()

    service = SmartHomeService(
        adapter=adapter,
    )

    await service.connect()
    await service.disconnect()

    assert service.connected is False
    adapter.disconnect.assert_awaited_once()