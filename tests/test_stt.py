import asyncio

from jarvis.audio.recorder import AudioRecorder
from jarvis.speech.stt import SpeechToText


async def main() -> None:
    recorder = AudioRecorder()
    stt = SpeechToText()

    print("กรุณาพูดหลังจากเริ่มอัดเสียง")
    print()

    audio_file = recorder.record(
        seconds=5.0,
        output="record.wav",
    )

    print()
    print("กำลังแปลงเสียงเป็นข้อความ...")

    text = await stt.transcribe(
        audio_file=audio_file,
        language="th",
    )

    print()
    print("=" * 50)
    print("Recognized Text")
    print("=" * 50)

    if text:
        print(text)
    else:
        print("[No speech detected]")

    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())