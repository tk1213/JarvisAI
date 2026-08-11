from __future__ import annotations

from pathlib import Path

from jarvis.audio.signal_diagnostics import AudioSignalAnalyzer


def main() -> None:
    path = Path(
        "tmp/audio/sprint5_pack_c_microphone.wav"
    )

    if not path.exists():
        raise FileNotFoundError(
            "Microphone recording was not found. "
            "Run tools/test_microphone_capture_live.py first."
        )

    result = AudioSignalAnalyzer().analyze(
        path
    )

    print("Sprint 5 Pack D — Microphone Signal Diagnostics")
    print("-" * 60)
    print(
        f"File: {result.path}"
    )
    print(
        f"Sample rate: {result.sample_rate} Hz"
    )
    print(
        f"Channels: {result.channels}"
    )
    print(
        f"Frames: {result.frames}"
    )
    print(
        f"RMS: {result.rms:.6f}"
    )
    print(
        f"Peak: {result.peak:.6f}"
    )
    print(
        f"Status: {result.status.value}"
    )
    print(
        f"Usable for STT: {result.usable_for_stt}"
    )

    if result.status.value == "silent":
        raise RuntimeError(
            "Recorded microphone signal is silent."
        )

    if result.status.value == "clipping":
        raise RuntimeError(
            "Recorded microphone signal is clipping."
        )

    print("RMS diagnostics: PASS")
    print("Peak diagnostics: PASS")
    print("Silence detection: PASS")
    print("Clipping detection: PASS")
    print("Sprint 5 Pack D live gate: PASS")


if __name__ == "__main__":
    main()
