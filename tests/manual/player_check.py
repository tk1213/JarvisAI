import asyncio

from jarvis.audio.player import AudioPlayer
from jarvis.speech.tts import TextToSpeech


async def main():

    tts = TextToSpeech()

    file = await tts.generate(
        "สวัสดีครับ TK ยินดีต้อนรับสู่ JarvisAI",
        output="output.wav",
    )

    player = AudioPlayer()

    player.play(file)


if __name__ == "__main__":
    asyncio.run(main())