from __future__ import annotations

import asyncio

from jarvis.audio.recorder import AudioRecorder
from jarvis.services.stt_service import STTService
from jarvis.speech.stt import SpeechToText


async def main() -> None:
    print("=" * 60)
    print(" JarvisAI - Live Microphone → STT Test")
    print("=" * 60)

    recorder = AudioRecorder()
    stt_engine = SpeechToText()

    stt = STTService(
        recorder=recorder,
        stt=stt_engine,
    )

    print()
    print("Microphone ready.")
    print("พูดหลังจากเห็นข้อความ Recording...")
    print()
    print('แนะนำให้พูด: "เปิด Smart Plug"')
    print()

    text = await stt.listen(
        seconds=5.0,
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