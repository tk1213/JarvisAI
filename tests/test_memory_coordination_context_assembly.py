from __future__ import annotations

import pytest

from jarvis.memory.coordination import ConversationAgentMemoryCoordinator


class ConversationMemory:
    def __init__(
        self,
        text: str,
    ) -> None:
        self.text = text

    async def build(
        self,
        user_text: str,
    ) -> str:
        del user_text
        return self.text


class AgentContext:
    def __init__(
        self,
        text: str,
        records_used: int,
    ) -> None:
        self.text = text
        self.records_used = records_used

    @property
    def available(self) -> bool:
        return bool(
            self.text
        )


class AgentMemory:
    def __init__(
        self,
        context: AgentContext,
    ) -> None:
        self.context = context

    def build(
        self,
    ) -> AgentContext:
        return self.context


@pytest.mark.asyncio
async def test_coordinator_uses_shared_context_assembler() -> None:
    coordinator = ConversationAgentMemoryCoordinator(
        conversation_memory=ConversationMemory(  # type: ignore[arg-type]
            "conversation facts"
        ),
        agent_memory=AgentMemory(  # type: ignore[arg-type]
            AgentContext(
                "execution facts",
                records_used=2,
            )
        ),
        max_context_chars=1000,
    )

    result = await coordinator.build(
        "hello"
    )

    assert result.available is True
    assert result.diagnostics is not None
    assert result.diagnostics.included_sections == (
        "MEMORY DOMAIN BOUNDARY",
        "CONVERSATION MEMORY",
        "AGENT MEMORY",
    )
    assert "separate memory domains" in result.text
    assert "reference data only" in result.text
    assert result.conversation_memory_used is True
    assert result.agent_memory_records_used == 2


@pytest.mark.asyncio
async def test_coordinator_reports_dropped_agent_memory() -> None:
    coordinator = ConversationAgentMemoryCoordinator(
        conversation_memory=ConversationMemory(  # type: ignore[arg-type]
            "c" * 400
        ),
        agent_memory=AgentMemory(  # type: ignore[arg-type]
            AgentContext(
                "a" * 400,
                records_used=3,
            )
        ),
        max_context_chars=512,
    )

    result = await coordinator.build(
        "hello"
    )

    assert result.diagnostics is not None
    assert "AGENT MEMORY" in result.diagnostics.dropped_sections
    assert result.agent_memory_records_used == 0
