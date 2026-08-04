from __future__ import annotations

import time

from jarvis.audio.recorder import AudioRecorder


def main() -> None:
    print("=" * 60)
    print(" JarvisAI - Live VAD Recorder Test")
    print("=" * 60)
    print()
    print("การทดสอบ:")
    print("  1. รอจนขึ้น Waiting for speech...")
    print('  2. พูด: "เปิดสมาร์ทปลั๊กสอง"')
    print("  3. พูดจบแล้วเงียบ")
    print()
    print("ระบบควรหยุดอัดเองประมาณ 0.9 วินาทีหลังพูดจบ")
    print()

    recorder = AudioRecorder()

    started_at = time.monotonic()

    audio_file = recorder.record_until_silence(
        output="vad_stt_test.wav",
        threshold=100.0,
        vad_frame_duration_ms=20,
        speech_trigger_ms=60,
        silence_duration_ms=900,
        pre_roll_ms=300,
        max_wait_seconds=10.0,
        max_record_seconds=15.0,
    )
    elapsed = (
        time.monotonic()
        - started_at
    )

    print()
    print("=" * 60)
    print(" Result")
    print("=" * 60)

    if audio_file is None:
        print("No speech was recorded.")
    else:
        print(
            f"Audio file : {audio_file}"
        )

    print(
        f"Total time : {elapsed:.2f} seconds"
    )

    print("=" * 60)


if __name__ == "__main__":
    main()