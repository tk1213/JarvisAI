import asyncio

from jarvis.audio.player import AudioPlayer
from jarvis.speech.tts import TextToSpeech


async def main() -> None:
    tts = TextToSpeech()
    player = AudioPlayer()

    output_file = await tts.generate(
        text="สวัสดีครับ TK ยินดีต้อนรับสู่ JarvisAI",
        output="output.wav",
    )

    print(f"Audio file: {output_file}")
    print("Playing audio...")

    player.play(output_file)

    print("Playback finished.")


if __name__ == "__main__":
    asyncio.run(main())