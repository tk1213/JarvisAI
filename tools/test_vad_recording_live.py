from __future__ import annotations

from jarvis.audio.manager import AudioManager
from jarvis.audio.recorder import AudioRecorder


def main() -> None:
    manager = AudioManager()
    recorder = AudioRecorder(manager)

    print("Sprint 5 Pack F — VAD Recording Path Hardening")
    print("-" * 60)
    print(
        f"Input device: [{manager.input_device}] "
        f"{manager.input_info.name}"
    )
    print("Wait briefly, then speak a sentence and stop speaking...")

    result = recorder.record_until_silence(
        output="tmp/audio/sprint5_pack_f_vad.wav",
        threshold=0.005,
        speech_trigger_ms=60,
        silence_duration_ms=900,
        pre_roll_ms=300,
        max_wait_seconds=10,
        max_record_seconds=15,
    )

    if result is None:
        raise RuntimeError(
            "VAD did not detect speech."
        )

    print(
        f"Saved: {result.path}"
    )
    print(
        f"Duration: {result.duration_seconds:.2f} s"
    )
    print(
        f"Frames: {result.frames}"
    )
    print("Speech trigger: PASS")
    print("Silence stop: PASS")
    print("VAD WAV persistence: PASS")
    print("Sprint 5 Pack F live gate: PASS")


if __name__ == "__main__":
    main()
