from __future__ import annotations

import pytest

from jarvis.services.conversation_manager import ConversationManager


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Jarvis version", "system.version"),
        ("เวอร์ชัน", "system.version"),
        ("เวอร์ชั่น", "system.version"),
        ("ทดสอบระบบ", "system.ping"),
        ("ระบบทำงานไหม", "system.ping"),
        ("health", "system.health"),
        ("health check", "system.health"),
        ("ตรวจสุขภาพระบบ", "system.health"),
        ("สถานะระบบตอนนี้เป็นอย่างไร", "system.health"),
    ],
)
def test_system_fast_path_intents_are_resolved(
    text: str,
    expected: str,
) -> None:
    assert (
        ConversationManager._resolve_system_capability(text)
        == expected
    )


@pytest.mark.parametrize(
    "text",
    [
        "what version of Python should I use",
        "this library has a new version",
        "the system design looks good",
        "health insurance information",
        "ping pong rules",
    ],
)
def test_non_system_intents_are_not_resolved(
    text: str,
) -> None:
    assert (
        ConversationManager._resolve_system_capability(text)
        is None
    )