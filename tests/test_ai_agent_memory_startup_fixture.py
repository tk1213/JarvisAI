from __future__ import annotations

from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, Mock

import pytest

from jarvis.agent.memory_repository import AIAgentMemoryRepository


@asynccontextmanager
async def empty_database_session():
    session = AsyncMock()

    result = Mock()
    mappings = Mock()
    mappings.all.return_value = []
    result.mappings.return_value = mappings

    session.execute = AsyncMock(
        return_value=result
    )

    yield session


class FakeDatabase:
    session = staticmethod(
        empty_database_session
    )


@pytest.mark.asyncio
async def test_repository_accepts_lifecycle_database_fixture() -> None:
    repository = AIAgentMemoryRepository(
        FakeDatabase(),  # type: ignore[arg-type]
    )

    records = await repository.list_recent()

    assert records == ()
