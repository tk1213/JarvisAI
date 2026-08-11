from __future__ import annotations

import asyncio

from jarvis.memory.coordination import ConversationAgentMemoryCoordinator


class ConversationMemory:
    async def build(
        self,
        user_text: str,
    ) -> str:
        del user_text

        return (
            "[Long-term memory]\n"
            "- personal: user_name = TK\n"
            "[End long-term memory]"
        )


class AgentContext:
    text = (
        "[Recent agent execution memory]\n"
        "- goal=Check Jarvis; success=True\n"
        "[End recent agent execution memory]"
    )
    records_used = 1

    @property
    def available(self) -> bool:
        return True


class AgentMemory:
    def build(
        self,
    ) -> AgentContext:
        return AgentContext()


async def main() -> None:
    coordinator = ConversationAgentMemoryCoordinator(
        conversation_memory=ConversationMemory(),  # type: ignore[arg-type]
        agent_memory=AgentMemory(),  # type: ignore[arg-type]
        max_context_chars=1000,
    )

    context = await coordinator.build(
        "What do you remember?"
    )

    assert context.available is True
    assert context.conversation_memory_used is True
    assert context.agent_memory_records_used == 1
    assert "user_name = TK" in context.text
    assert "goal=Check Jarvis" in context.text
    assert "separate memory domains" in context.text
    assert len(context.text) <= 1000

    print("Sprint 4.4 Pack C — Conversation / Agent Memory Coordination")
    print("-" * 60)
    print("Separate memory domains: PASS")
    print("Coordinated context: PASS")
    print("Instruction boundary: PASS")
    print("Combined context budget: PASS")
    print("Sprint 4.4 Pack C live gate: PASS")


if __name__ == "__main__":
    asyncio.run(
        main()
    )
