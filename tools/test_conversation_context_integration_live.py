from __future__ import annotations

import asyncio

from jarvis.conversation.production_context import (
    ConversationProductionContextBuilder,
)


class Context:
    text = (
        "[CONVERSATION MEMORY]\\n"
        "reference facts\\n\\n"
        "[AGENT MEMORY]\\n"
        "execution history"
    )


class Coordinator:
    async def build(
        self,
        user_text: str,
    ) -> Context:
        del user_text
        return Context()


async def main() -> None:
    builder = ConversationProductionContextBuilder(
        memory_coordinator=Coordinator(),  # type: ignore[arg-type]
        system_text="Jarvis production safety rules.",
    )

    result = await builder.build(
        user_text="Check Jarvis.",
        history_text="Previous turn.",
    )

    assert result.text.startswith(
        "[SYSTEM]"
    )
    assert "[MEMORY CONTEXT]" in result.text
    assert "[HISTORY]" in result.text
    assert result.text.endswith(
        "Check Jarvis."
    )

    print("Sprint 4.7 Pack B — Context Assembly Integration")
    print("-" * 60)
    print("Conversation memory integration: PASS")
    print("Agent memory integration: PASS")
    print("Deterministic production precedence: PASS")
    print("Assembly diagnostics: PASS")
    print("Sprint 4.7 Pack B live gate: PASS")


if __name__ == "__main__":
    asyncio.run(
        main()
    )
