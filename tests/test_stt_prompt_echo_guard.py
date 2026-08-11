from jarvis.speech.stt import SpeechToText


def test_thai_stt_rejects_prompt_echo_prefix() -> None:
    assert SpeechToText._is_suspicious_transcript(
        text="บทสนทนาภาษาไทยกับผู้ช่วย JarvisAI",
        language="th",
    )


def test_thai_stt_keeps_real_user_speech() -> None:
    assert not SpeechToText._is_suspicious_transcript(
        text="วันนี้วันอะไร",
        language="th",
    )