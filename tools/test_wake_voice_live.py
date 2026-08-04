from __future__ import annotations

import asyncio

from jarvis.core.application import JarvisApplication
from jarvis.core.container import container
from jarvis.services.conversation_manager import ConversationManager
from jarvis.services.voice_service import VoiceService
from jarvis.services.wake_word_service import WakeWordService


async def main() -> None:
    print("=" * 60)
    print(" JarvisAI - Wake Word → Voice Multi-turn Test")
    print("=" * 60)
    print()
    print("WARNING: This test can control real Tuya devices.")
    print()
    print("ตัวอย่างการทดสอบ:")
    print('  1. พูด: "Hey Jarvis"')
    print('  2. พูด: "เปิดปลั๊ก"')
    print('  3. Jarvis ถามเลือกอุปกรณ์')
    print('  4. พูด: "สมาร์ทปลั๊กสอง"')
    print()
    print(
        'ไม่ต้องพูด "Hey Jarvis" ซ้ำ'
        " ระหว่าง clarification"
    )
    print()
    print("กด Ctrl+C เพื่อหยุด")
    print()

    app = JarvisApplication()

    try:
        await app.start(
            start_background_tasks=False,
        )

        wake_word = container.resolve(
            "wake_word",
            WakeWordService,
        )

        voice = container.resolve(
            "voice",
            VoiceService,
        )

        conversation = container.resolve(
            "conversation",
            ConversationManager,
        )

        while True:
            print()
            print("-" * 60)
            print(
                'Waiting for wake word: "Hey Jarvis"...'
            )
            print("-" * 60)

            score = await wake_word.wait_for_wake_word()

            print()
            print(
                "Wake word detected "
                f"(score={score:.4f})"
            )

            print()
            print("Listening for command...")

            reply = await voice.listen_and_reply(
                language="th",
            )

            if not reply:
                print()
                print(
                    "No command detected. "
                    "Returning to wake mode."
                )
                continue

            while conversation.has_pending_smart_home:
                print()
                print(
                    "Waiting for clarification..."
                )

                clarification_reply = (
                    await voice.listen_and_reply(
                        language="th",
                    )
                )

                if not clarification_reply:
                    print()
                    print(
                        "No clarification detected."
                    )
                    continue

            print()
            print(
                "Conversation complete. "
                "Returning to wake mode."
            )

    except KeyboardInterrupt:
        print()
        print(
            "Wake voice test stopped by user."
        )

    except asyncio.CancelledError:
        print()
        print(
            "Wake voice test cancelled."
        )

    finally:
        await app.shutdown()


if __name__ == "__main__":
    asyncio.run(main())