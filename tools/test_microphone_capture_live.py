from __future__ import annotations

from pathlib import Path

from jarvis.audio.manager import AudioManager
from jarvis.audio.recorder import AudioRecorder


def main() -> None:
    manager = AudioManager()
    recorder = AudioRecorder(
        manager
    )

    output = Path(
        "tmp/audio/sprint5_pack_c_microphone.wav"
    )

    print("Sprint 5 Pack C — Production Microphone Capture")
    print("-" * 60)
    print(
        f"Input device: [{manager.input_device}] "
        f"{manager.input_info.name}"
    )
    print(
        "Recording 5 seconds. Speak into the microphone now..."
    )

    result = recorder.record(
        output,
        seconds=5.0,
        channels=1,
    )

    assert result.path.exists()
    assert result.frames > 0
    assert result.duration_seconds > 4.9

    print()
    print(
        f"Saved: {result.path}"
    )
    print(
        f"Sample rate: {result.sample_rate} Hz"
    )
    print(
        f"Frames: {result.frames}"
    )
    print(
        f"Duration: {result.duration_seconds:.2f} s"
    )
    print("Microphone fixed-duration capture: PASS")
    print("WAV persistence: PASS")
    print("Selected-device usage: PASS")
    print("Sprint 5 Pack C live gate: PASS")


if __name__ == "__main__":
    main()
