from __future__ import annotations

from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, Mock

import pytest

from jarvis.agent.memory_repository import AIAgentMemoryRepository


@asynccontextmanager
async def lifecycle_database_session():
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


class FakeDatabase:
    session = staticmethod(
        lifecycle_database_session
    )


@pytest.mark.asyncio
async def test_lifecycle_fixture_supports_list_recent_and_count() -> None:
    repository = AIAgentMemoryRepository(
        FakeDatabase(),  # type: ignore[arg-type]
    )

    records = await repository.list_recent()
    count = await repository.count()

    assert records == ()
    assert count == 0
