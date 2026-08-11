from __future__ import annotations

import pytest

from jarvis.services.conversation_manager import ConversationManager


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("วันนี้วันอะไร", "system.datetime"),
        ("วันนี้วันที่เท่าไหร่", "system.datetime"),
        ("วันนี้วันที่อะไร", "system.datetime"),
        ("วันนี้วันไหน", "system.datetime"),
        ("ตอนนี้กี่โมง", "system.datetime"),
        ("ตอนนี้เวลาอะไร", "system.datetime"),
        ("เวลาเท่าไหร่", "system.datetime"),
        ("what time is it", "system.datetime"),
        ("what day is it", "system.datetime"),
        ("what's the date today", "system.datetime"),
    ],
)
def test_datetime_intents_are_resolved(
    text: str,
    expected: str,
) -> None:
    assert (
        ConversationManager._resolve_system_capability(
            text
        )
        == expected
    )


@pytest.mark.parametrize(
    "text",
    [
        "I had a good time yesterday",
        "this project will take time",
        "update the database",
        "today we should test the microphone",
        "date format in Python",
    ],
)
def test_non_datetime_intents_are_not_resolved(
    text: str,
) -> None:
    assert (
        ConversationManager._resolve_system_capability(
            text
        )
        is None
    )