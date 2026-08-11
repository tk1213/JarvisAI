from jarvis.services.conversation_manager import ConversationManager


def test_voice_reply_guard_shortens_simple_food_recommendation() -> None:
    reply = ConversationManager._guard_voice_reply(
        user_text="เย็นนี้กินอะไรดี",
        reply=(
            "ครับ TK, เย็นนี้แนะนำสุกี้น้ำทะเลครับ "
            "อุ่นท้องและกินง่ายครับ"
        ),
    )

    assert reply == (
        "ครับ TK, เย็นนี้แนะนำสุกี้น้ำทะเลครับ"
    )


def test_voice_reply_guard_keeps_detail_request() -> None:
    original = (
        "ครับ TK, แนะนำสุกี้น้ำทะเลครับ "
        "เพราะอุ่นท้องและกินง่ายครับ"
    )

    reply = ConversationManager._guard_voice_reply(
        user_text="เย็นนี้กินอะไรดี อธิบายด้วยว่าทำไม",
        reply=original,
    )

    assert reply == original


def test_voice_reply_guard_keeps_non_recommendation_reply() -> None:
    original = (
        "ครับ TK, วันนี้อากาศค่อนข้างร้อนครับ "
        "ควรดื่มน้ำให้เพียงพอครับ"
    )

    reply = ConversationManager._guard_voice_reply(
        user_text="วันนี้อากาศเป็นยังไง",
        reply=original,
    )

    assert reply == original


def test_voice_reply_guard_handles_empty_reply() -> None:
    reply = ConversationManager._guard_voice_reply(
        user_text="เย็นนี้กินอะไรดี",
        reply="",
    )

    assert reply == ""


def test_voice_reply_guard_supports_english_recommendation() -> None:
    reply = ConversationManager._guard_voice_reply(
        user_text="what should i eat",
        reply=(
            "I recommend chicken rice. "
            "It is simple and filling."
        ),
    )

    assert reply == (
        "I recommend chicken rice. "
        "It is simple and filling."
    )