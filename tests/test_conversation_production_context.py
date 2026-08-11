from __future__ import annotations

import pytest

from jarvis.conversation.production_context import (
    ConversationProductionContextBuilder,
)


class Coordinated:
    text = (
        "[CONVERSATION MEMORY]\\n"
        "memory facts\\n\\n"
        "[AGENT MEMORY]\\n"
        "agent facts"
    )


class Coordinator:
    async def build(
        self,
        user_text: str,
    ) -> Coordinated:
        del user_text
        return Coordinated()


@pytest.mark.asyncio
async def test_production_context_has_deterministic_precedence() -> None:
    builder = ConversationProductionContextBuilder(
        memory_coordinator=Coordinator(),  # type: ignore[arg-type]
        system_text="system rules",
    )

    result = await builder.build(
        user_text="hello",
        history_text="prior conversation",
    )

    text = result.text

    assert text.index(
        "[SYSTEM]"
    ) < text.index(
        "[MEMORY CONTEXT]"
    )
    assert text.index(
        "[MEMORY CONTEXT]"
    ) < text.index(
        "[HISTORY]"
    )
    assert text.index(
        "[HISTORY]"
    ) < text.index(
        "[CURRENT USER]"
    )


@pytest.mark.asyncio
async def test_current_user_is_required() -> None:
    builder = ConversationProductionContextBuilder(
        memory_coordinator=Coordinator(),  # type: ignore[arg-type]
    )

    result = await builder.build(
        user_text="hello"
    )

    assert "CURRENT USER" in result.assembly.diagnostics.included_sections
