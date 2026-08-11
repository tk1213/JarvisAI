from __future__ import annotations

import pytest

from jarvis.memory.coordination import ConversationAgentMemoryCoordinator


class ConversationMemory:
    async def build(
        self,
        user_text: str,
    ) -> str:
        del user_text

        return "conversation facts"


class AgentContext:
    text = "agent facts"
    records_used = 1

    @property
    def available(self) -> bool:
        return True


class AgentMemory:
    def build(
        self,
    ) -> AgentContext:
        return AgentContext()


@pytest.mark.asyncio
async def test_diagnostics_include_memory_domain_boundary() -> None:
    result = await ConversationAgentMemoryCoordinator(
        conversation_memory=ConversationMemory(),  # type: ignore[arg-type]
        agent_memory=AgentMemory(),  # type: ignore[arg-type]
    ).build(
        "hello"
    )

    assert result.diagnostics is not None
    assert result.diagnostics.included_sections == (
        "MEMORY DOMAIN BOUNDARY",
        "CONVERSATION MEMORY",
        "AGENT MEMORY",
    )
