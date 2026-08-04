from __future__ import annotations

import asyncio

from jarvis.core.application import JarvisApplication
from jarvis.core.container import container
from jarvis.services.voice_service import VoiceService


async def main() -> None:
    print("=" * 60)
    print(" JarvisAI - Live Voice → Tuya Test")
    print("=" * 60)

    print()
    print("WARNING: This test controls a real Tuya device.")
    print()
    print("พูดหลังจากเห็น Recording...")
    print('แนะนำให้พูด: "เปิดสมาร์ทปลั๊ก"')
    print()

    app = JarvisApplication()

    try:
        await app.start(
            start_background_tasks=False,
        )

        voice = container.resolve(
            "voice",
            VoiceService,
        )

        reply = await voice.listen_and_reply(
            seconds=5.0,
            language="th",
        )

        print()
        print("=" * 60)
        print(" Voice Test Result")
        print("=" * 60)
        print(f"Reply: {reply!r}")

    finally:
        await app.shutdown()


if __name__ == "__main__":
    asyncio.run(main())