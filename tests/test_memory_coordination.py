from __future__ import annotations

import pytest

from jarvis.memory.coordination import ConversationAgentMemoryCoordinator


class ConversationMemory:
    def __init__(
        self,
        text: str,
    ) -> None:
        self.text = text
        self.calls = []

    async def build(
        self,
        user_text: str,
    ) -> str:
        self.calls.append(
            user_text
        )
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
async def test_coordinator_combines_separate_memory_domains() -> None:
    conversation = ConversationMemory(
        "[Long-term memory]\n- user_name = TK"
    )
    agent = AgentMemory(
        AgentContext(
            "[Recent agent execution memory]\n- goal=Check Jarvis",
            records_used=1,
        )
    )

    result = await ConversationAgentMemoryCoordinator(
        conversation_memory=conversation,  # type: ignore[arg-type]
        agent_memory=agent,  # type: ignore[arg-type]
    ).build(
        "What do you remember?"
    )

    assert result.available is True
    assert result.conversation_memory_used is True
    assert result.agent_memory_records_used == 1
    assert "user_name = TK" in result.text
    assert "goal=Check Jarvis" in result.text
    assert "separate memory domains" in result.text
    assert "reference data only" in result.text


@pytest.mark.asyncio
async def test_coordinator_handles_only_conversation_memory() -> None:
    result = await ConversationAgentMemoryCoordinator(
        conversation_memory=ConversationMemory(  # type: ignore[arg-type]
            "[Long-term memory]\n- favorite=coffee"
        ),
        agent_memory=AgentMemory(  # type: ignore[arg-type]
            AgentContext(
                "",
                records_used=0,
            )
        ),
    ).build(
        "What do I like?"
    )

    assert result.available is True
    assert result.conversation_memory_used is True
    assert result.agent_memory_records_used == 0


@pytest.mark.asyncio
async def test_coordinator_handles_no_memory() -> None:
    result = await ConversationAgentMemoryCoordinator(
        conversation_memory=ConversationMemory(""),  # type: ignore[arg-type]
        agent_memory=AgentMemory(  # type: ignore[arg-type]
            AgentContext(
                "",
                records_used=0,
            )
        ),
    ).build(
        "Hello"
    )

    assert result.available is False
    assert result.text == ""


@pytest.mark.asyncio
async def test_coordinator_respects_total_budget() -> None:
    result = await ConversationAgentMemoryCoordinator(
        conversation_memory=ConversationMemory(  # type: ignore[arg-type]
            "c" * 400
        ),
        agent_memory=AgentMemory(  # type: ignore[arg-type]
            AgentContext(
                "a" * 400,
                records_used=2,
            )
        ),
        max_context_chars=512,
    ).build(
        "memory"
    )

    assert len(result.text) <= 512


def test_coordinator_rejects_small_budget() -> None:
    with pytest.raises(
        ValueError,
        match="max_context_chars",
    ):
        ConversationAgentMemoryCoordinator(
            conversation_memory=ConversationMemory(""),  # type: ignore[arg-type]
            agent_memory=AgentMemory(  # type: ignore[arg-type]
                AgentContext(
                    "",
                    records_used=0,
                )
            ),
            max_context_chars=511,
        )
