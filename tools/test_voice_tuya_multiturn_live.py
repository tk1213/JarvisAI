from __future__ import annotations

import asyncio

from jarvis.core.application import JarvisApplication
from jarvis.core.container import container
from jarvis.services.voice_service import VoiceService


async def main() -> None:
    print("=" * 60)
    print(" JarvisAI - Voice Multi-turn → Tuya Test")
    print("=" * 60)

    print()
    print("WARNING: This test can control real Tuya devices.")
    print()
    print("รอบแรก พูด:")
    print('  "เปิดปลั๊ก"')
    print()
    print("จากนั้น Jarvis จะถามเลือกอุปกรณ์")
    print()
    print("รอบที่สอง พูด:")
    print('  "ห้องนอน"')
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

        print()
        print("=" * 60)
        print(" STEP 1 - Initial command")
        print("=" * 60)

        first_reply = await voice.listen_and_reply(
            seconds=5.0,
            language="th",
        )

        print()
        print(
            f"First reply: {first_reply!r}"
        )

        if not first_reply:
            raise RuntimeError(
                "No reply returned from first voice turn."
            )

        print()
        print("=" * 60)
        print(" STEP 2 - Clarification")
        print("=" * 60)

        print()
        print("เตรียมพูดคำตอบ เช่น:")
        print('  "ห้องนอน"')
        print()

        second_reply = await voice.listen_and_reply(
            seconds=5.0,
            language="th",
        )

        print()
        print(
            f"Second reply: {second_reply!r}"
        )

        if not second_reply:
            raise RuntimeError(
                "No reply returned from second voice turn."
            )

        print()
        print("=" * 60)
        print(" Multi-turn Voice Test Complete")
        print("=" * 60)

    finally:
        await app.shutdown()


if __name__ == "__main__":
    asyncio.run(main())