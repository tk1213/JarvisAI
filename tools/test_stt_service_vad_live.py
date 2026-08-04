from __future__ import annotations

import asyncio

from jarvis.audio.recorder import AudioRecorder
from jarvis.services.stt_service import STTService
from jarvis.speech.stt import SpeechToText


async def main() -> None:
    print("=" * 60)
    print(" JarvisAI - STTService VAD Live Test")
    print("=" * 60)
    print()
    print("รอจนขึ้น Waiting for speech...")
    print()
    print('แนะนำให้พูด: "เปิดสมาร์ทปลั๊กสอง"')
    print()

    recorder = AudioRecorder()
    stt_engine = SpeechToText()

    stt_service = STTService(
        recorder=recorder,
        stt=stt_engine,
    )

    text = await stt_service.listen(
        language="th",
    )

    print()
    print("=" * 60)
    print(" Result")
    print("=" * 60)
    print(f"Transcript: {text!r}")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())