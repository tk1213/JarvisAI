from __future__ import annotations

import statistics
import time

from jarvis.audio.stream import AudioStream
from jarvis.audio.vad import VoiceActivityDetector


def main() -> None:
    print("=" * 60)
    print(" JarvisAI - Live VAD Calibration")
    print("=" * 60)
    print()
    print("Phase 1: เงียบ 5 วินาที")
    print("Phase 2: พูดตามปกติ 5 วินาที")
    print()

    stream = AudioStream(
        frame_duration_ms=20,
    )

    vad = VoiceActivityDetector(
        threshold=500.0,
    )

    frame_iterator = stream.frames()

    quiet_values: list[float] = []
    speech_values: list[float] = []

    print("-" * 60)
    print("PHASE 1 - QUIET")
    print("-" * 60)
    print("กรุณาเงียบ...")

    quiet_end = time.monotonic() + 5.0

    while time.monotonic() < quiet_end:
        frame = next(
            frame_iterator
        )

        result = vad.analyze(
            frame
        )

        quiet_values.append(
            result.rms
        )

    print()
    print("-" * 60)
    print("PHASE 2 - SPEAK")
    print("-" * 60)
    print("พูดตามปกติ เช่น:")
    print('"Jarvis เปิดปลั๊กห้องนั่งเล่น"')

    speech_end = time.monotonic() + 5.0

    while time.monotonic() < speech_end:
        frame = next(
            frame_iterator
        )

        result = vad.analyze(
            frame
        )

        speech_values.append(
            result.rms
        )

    quiet_average = statistics.mean(
        quiet_values
    )

    quiet_max = max(
        quiet_values
    )

    speech_average = statistics.mean(
        speech_values
    )

    speech_max = max(
        speech_values
    )

    recommended_threshold = max(
        quiet_max * 2.0,
        quiet_average * 3.0,
    )

    print()
    print("=" * 60)
    print(" Calibration Result")
    print("=" * 60)

    print(
        f"Quiet average       : "
        f"{quiet_average:.2f}"
    )
    print(
        f"Quiet maximum       : "
        f"{quiet_max:.2f}"
    )

    print(
        f"Speech average      : "
        f"{speech_average:.2f}"
    )
    print(
        f"Speech maximum      : "
        f"{speech_max:.2f}"
    )

    print(
        f"Recommended threshold: "
        f"{recommended_threshold:.2f}"
    )

    print("=" * 60)


if __name__ == "__main__":
    main()