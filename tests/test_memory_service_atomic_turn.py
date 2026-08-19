from __future__ import annotations

from unittest.mock import AsyncMock, Mock

import pytest

from jarvis.services.memory_service import MemoryService


@pytest.mark.asyncio
async def test_save_turn_adds_user_and_assistant_in_one_session() -> None:
    database = Mock()

    session = Mock()
    session.add = Mock()

    context = AsyncMock()
    context.__aenter__.return_value = session
    context.__aexit__.return_value = None

    database.session.return_value = context

    service = MemoryService(
        database=database,
    )

    await service.save_turn(
        user_content="hello",
        assistant_content="hi",
    )

    database.session.assert_called_once_with()

    assert session.add.call_count == 2

    first = session.add.call_args_list[0].args[0]
    second = session.add.call_args_list[1].args[0]

    assert first.role == "user"
    assert first.content == "hello"

    assert second.role == "assistant"
    assert second.content == "hi"

@pytest.mark.asyncio
async def test_save_turn_uses_single_transaction_for_atomic_rollback() -> None:
    database = Mock()

    session = Mock()
    session.add = Mock()

    context = AsyncMock()
    context.__aenter__.return_value = session
    context.__aexit__.return_value = None

    database.session.return_value = context

    service = MemoryService(
        database=database,
    )

    await service.save_turn(
        user_content="hello",
        assistant_content="hi",
    )

    database.session.assert_called_once_with()
    assert session.add.call_count == 2