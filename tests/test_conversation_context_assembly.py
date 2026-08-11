from __future__ import annotations

import pytest

from jarvis.conversation.context_assembly import (
    ConversationContextAssembler,
    ConversationContextPriority,
    ConversationContextSection,
)


def section(
    name: str,
    text: str,
    priority: ConversationContextPriority,
    *,
    required: bool = False,
) -> ConversationContextSection:
    return ConversationContextSection(
        name=name,
        text=text,
        priority=priority,
        required=required,
    )


def test_assembler_uses_deterministic_priority_order() -> None:
    result = ConversationContextAssembler().assemble(
        (
            section(
                "CURRENT USER",
                "hello",
                ConversationContextPriority.CURRENT_USER,
                required=True,
            ),
            section(
                "SYSTEM",
                "system rules",
                ConversationContextPriority.SYSTEM,
                required=True,
            ),
            section(
                "HISTORY",
                "prior turn",
                ConversationContextPriority.HISTORY,
            ),
        )
    )

    assert result.text.index(
        "[SYSTEM]"
    ) < result.text.index(
        "[HISTORY]"
    )
    assert result.text.index(
        "[HISTORY]"
    ) < result.text.index(
        "[CURRENT USER]"
    )


def test_optional_sections_are_dropped_when_budget_is_full() -> None:
    assembler = ConversationContextAssembler(
        max_chars=512
    )

    result = assembler.assemble(
        (
            section(
                "SYSTEM",
                "s" * 100,
                ConversationContextPriority.SYSTEM,
                required=True,
            ),
            section(
                "MEMORY",
                "m" * 1000,
                ConversationContextPriority.CONVERSATION_MEMORY,
            ),
            section(
                "CURRENT USER",
                "hello",
                ConversationContextPriority.CURRENT_USER,
                required=True,
            ),
        )
    )

    assert "MEMORY" in result.diagnostics.dropped_sections
    assert "SYSTEM" in result.diagnostics.included_sections
    assert "CURRENT USER" in result.diagnostics.included_sections
    assert len(result.text) <= 512


def test_required_section_over_budget_is_rejected() -> None:
    assembler = ConversationContextAssembler(
        max_chars=512
    )

    with pytest.raises(
        ValueError,
        match="Required context section",
    ):
        assembler.assemble(
            (
                section(
                    "SYSTEM",
                    "x" * 1000,
                    ConversationContextPriority.SYSTEM,
                    required=True,
                ),
            )
        )


def test_empty_sections_are_ignored() -> None:
    result = ConversationContextAssembler().assemble(
        (
            section(
                "EMPTY",
                "   ",
                ConversationContextPriority.HISTORY,
            ),
            section(
                "CURRENT USER",
                "hello",
                ConversationContextPriority.CURRENT_USER,
                required=True,
            ),
        )
    )

    assert "EMPTY" not in result.diagnostics.included_sections
    assert result.diagnostics.included_sections == (
        "CURRENT USER",
    )


def test_diagnostics_report_remaining_budget() -> None:
    result = ConversationContextAssembler(
        max_chars=1000
    ).assemble(
        (
            section(
                "CURRENT USER",
                "hello",
                ConversationContextPriority.CURRENT_USER,
                required=True,
            ),
        )
    )

    assert result.diagnostics.used_chars == len(
        result.text
    )
    assert result.diagnostics.remaining_chars == (
        1000 - len(result.text)
    )


def test_invalid_budget_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="max_chars",
    ):
        ConversationContextAssembler(
            max_chars=511
        )
