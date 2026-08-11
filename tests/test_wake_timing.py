from __future__ import annotations

from jarvis.wake.timing import TurnTiming


def test_turn_timing_starts_empty() -> None:
    timing = TurnTiming()

    assert timing.wake_detected_at is None
    assert timing.acknowledgement_done_at is None
    assert timing.transcript_ready_at is None
    assert timing.conversation_done_at is None
    assert timing.tts_done_at is None

    assert timing.wake_seconds is None
    assert timing.total_seconds is None


def test_turn_timing_records_all_stages() -> None:
    timing = TurnTiming()

    timing.mark_wake_detected()
    timing.mark_acknowledgement_done()
    timing.mark_transcript_ready()
    timing.mark_conversation_done()
    timing.mark_tts_done()

    assert timing.wake_seconds is not None
    assert timing.acknowledgement_seconds is not None
    assert timing.command_capture_seconds is not None
    assert timing.conversation_seconds is not None
    assert timing.tts_seconds is not None
    assert timing.total_seconds is not None

    assert timing.wake_seconds >= 0
    assert timing.acknowledgement_seconds >= 0
    assert timing.command_capture_seconds >= 0
    assert timing.conversation_seconds >= 0
    assert timing.tts_seconds >= 0
    assert timing.total_seconds >= 0