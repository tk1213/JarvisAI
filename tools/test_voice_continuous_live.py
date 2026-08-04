from __future__ import annotations

import asyncio

from jarvis.core.application import JarvisApplication
from jarvis.core.container import container
from jarvis.services.voice_service import VoiceService


async def main() -> None:
    print("=" * 60)
    print(" JarvisAI - Continuous Voice Live Test")
    print("=" * 60)

    print()
    print("WARNING: This test can control real Tuya devices.")
    print()
    print("ตัวอย่างการทดสอบ:")
    print('  1. "เปิดปลั๊ก"')
    print('  2. "สมาร์ทปลั๊กสอง"')
    print('  3. "ปิดสมาร์ทปลั๊กสอง"')
    print('  4. "หยุดจาร์วิส"')
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

        await voice.run_continuous(
            seconds=5.0,
            language="th",
            idle_delay=0.25,
        )

    except KeyboardInterrupt:
        print()
        print("Continuous voice test stopped by user.")

    finally:
        await app.shutdown()


if __name__ == "__main__":
    asyncio.run(main())