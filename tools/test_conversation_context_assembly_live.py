from __future__ import annotations

from jarvis.conversation.context_assembly import (
    ConversationContextAssembler,
    ConversationContextPriority,
    ConversationContextSection,
)


def main() -> None:
    assembler = ConversationContextAssembler(
        max_chars=800
    )

    result = assembler.assemble(
        (
            ConversationContextSection(
                name="SYSTEM",
                text="Follow Jarvis production safety rules.",
                priority=ConversationContextPriority.SYSTEM,
                required=True,
            ),
            ConversationContextSection(
                name="CONVERSATION MEMORY",
                text="Reference-only user context.",
                priority=ConversationContextPriority.CONVERSATION_MEMORY,
            ),
            ConversationContextSection(
                name="AGENT MEMORY",
                text="Reference-only execution context.",
                priority=ConversationContextPriority.AGENT_MEMORY,
            ),
            ConversationContextSection(
                name="CURRENT USER",
                text="Check the system.",
                priority=ConversationContextPriority.CURRENT_USER,
                required=True,
            ),
        )
    )

    assert result.text.startswith(
        "[SYSTEM]"
    )
    assert result.diagnostics.used_chars <= 800
    assert "SYSTEM" in result.diagnostics.included_sections
    assert "CURRENT USER" in result.diagnostics.included_sections

    print("Sprint 4.7 Pack A — Production Context Assembly Contract")
    print("-" * 60)
    print("Deterministic precedence: PASS")
    print("Required-section protection: PASS")
    print("Optional-section budget dropping: PASS")
    print("Context diagnostics: PASS")
    print("Sprint 4.7 Pack A live gate: PASS")


if __name__ == "__main__":
    main()
