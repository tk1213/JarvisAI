import asyncio

from jarvis.core.application import JarvisApplication
from jarvis.core.container import container


async def main() -> None:
    app = JarvisApplication()

    try:
        await app.start(start_background_tasks=False)

        voice = container.get("voice")

        print()
        print("=" * 60)
        print("Jarvis Voice Test")
        print("=" * 60)
        print("🎤 Speak after the prompt...")
        print()

        await voice.listen_and_reply()

    finally:
        await app.shutdown()


if __name__ == "__main__":
    asyncio.run(main())