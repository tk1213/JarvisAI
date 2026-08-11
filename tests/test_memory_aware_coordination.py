from __future__ import annotations

from unittest.mock import AsyncMock, Mock

import pytest

from jarvis.memory.aware_conversation import MemoryAwareConversationManager


class Coordinator:
    def __init__(
        self,
        text: str,
    ) -> None:
        self.text = text

    async def build(
        self,
        user_text: str,
    ):
        del user_text

        return Mock(
            text=self.text
        )


@pytest.mark.asyncio
async def test_memory_aware_conversation_prefers_coordinator() -> None:
    manager = object.__new__(
        MemoryAwareConversationManager
    )

    manager._memory_coordinator = Coordinator(  # type: ignore[attr-defined]
        "[Coordinated memory context]\nreference"
    )
    manager._memory_context = Mock()  # type: ignore[attr-defined]

    base = AsyncMock(
        return_value="reply"
    )

    # Exercise enrichment construction through a small bound replacement of
    # ConversationManager._ask_ai target.
    original = MemoryAwareConversationManager.__mro__[1]._ask_ai
    MemoryAwareConversationManager.__mro__[1]._ask_ai = base

    try:
        reply = await manager._ask_ai(
            "hello"
        )
    finally:
        MemoryAwareConversationManager.__mro__[1]._ask_ai = original

    assert reply == "reply"

    sent_text = base.await_args.args[0]

    assert "Coordinated memory context" in sent_text
    assert "[Current user message]" in sent_text
    assert sent_text.endswith(
        "hello"
    )
