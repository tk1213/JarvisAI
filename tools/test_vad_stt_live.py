from __future__ import annotations

import asyncio

from jarvis.audio.recorder import AudioRecorder
from jarvis.speech.stt import SpeechToText


async def main() -> None:
    print("=" * 60)
    print(" JarvisAI - Live VAD → STT Test")
    print("=" * 60)
    print()
    print("รอจนขึ้น Waiting for speech...")
    print()
    print('แนะนำให้พูด: "เปิดสมาร์ทปลั๊กสอง"')
    print()

    recorder = AudioRecorder()
    stt = SpeechToText()

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

    if audio_file is None:
        print()
        print("=" * 60)
        print(" STT Result")
        print("=" * 60)
        print("No speech detected.")
        print("=" * 60)
        return

    text = await stt.transcribe(
        audio_file=audio_file,
        language="th",
    )

    print()
    print("=" * 60)
    print(" STT Result")
    print("=" * 60)
    print(f"Transcript: {text!r}")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())