from __future__ import annotations

from jarvis.conversation.context_assembly import (
    ConversationContextAssembler,
    ConversationContextPriority,
    ConversationContextSection,
)


def test_required_and_optional_sections_keep_global_priority() -> None:
    result = ConversationContextAssembler().assemble(
        (
            ConversationContextSection(
                name="CURRENT USER",
                text="hello",
                priority=ConversationContextPriority.CURRENT_USER,
                required=True,
            ),
            ConversationContextSection(
                name="SYSTEM",
                text="rules",
                priority=ConversationContextPriority.SYSTEM,
                required=True,
            ),
            ConversationContextSection(
                name="HISTORY",
                text="previous turn",
                priority=ConversationContextPriority.HISTORY,
            ),
        )
    )

    assert result.diagnostics.included_sections == (
        "SYSTEM",
        "HISTORY",
        "CURRENT USER",
    )
