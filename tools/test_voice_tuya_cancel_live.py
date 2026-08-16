from __future__ import annotations

import asyncio

from jarvis.core.application import JarvisApplication
from jarvis.core.container import container
from jarvis.services.conversation_manager import ConversationManager
from jarvis.voice.dialogue_runtime import VoiceDialogueRuntime
from jarvis.voice.turn_runtime import VoiceTurnRuntime


async def main() -> None:
    print("=" * 60)
    print(" JarvisAI - Voice Tuya Cancellation Safety Gate")
    print("=" * 60)

    print()
    print("WARNING: This test targets a real Tuya device.")
    print()
    print("Use an online device whose initial state is OFF.")
    print()
    print("First speak clearly:")
    print('  "เปิด Smart plug 2"')
    print()
    print(
        "Wait until Jarvis FINISHES speaking the confirmation prompt."
    )
    print("Then speak clearly:")
    print('  "ยกเลิก"')
    print()

    app = JarvisApplication()

    await app.start(
        start_background_tasks=False,
    )

    try:
        voice_turn = container.resolve(
            "voice_turn",
            VoiceTurnRuntime,
        )

        conversation = container.resolve(
            "conversation",
            ConversationManager,
        )

        runtime = VoiceDialogueRuntime(
            voice_turn=voice_turn,
            conversation=conversation,
            max_follow_ups=2,
        )

        result = await runtime.run(
            language="th",
        )

        for index, turn in enumerate(
            result.turns,
            start=1,
        ):
            print()
            print(
                f"Turn {index} status     : "
                f"{turn.status.value}"
            )
            print(
                f"Turn {index} transcript : "
                f"{turn.transcript!r}"
            )
            print(
                f"Turn {index} reply      : "
                f"{turn.reply!r}"
            )

        print()
        print(
            f"Follow-ups used    : "
            f"{result.follow_ups_used}"
        )
        print(
            f"Pending smart home : "
            f"{result.pending_smart_home}"
        )

        if len(result.turns) < 2:
            raise RuntimeError(
                "Cancellation follow-up was not captured."
            )

        cancel_turn = result.turns[1]

        if not cancel_turn.transcript:
            raise RuntimeError(
                "Cancellation speech was not detected."
            )

        if result.pending_smart_home:
            raise RuntimeError(
                "Smart Home command remained pending after cancellation."
            )

        if not result.completed:
            raise RuntimeError(
                "Voice cancellation dialogue did not complete."
            )

        print()
        print("Voice command capture        : PASS")
        print("Cancellation speech capture  : PASS")
        print("Pending confirmation cleared : PASS")
        print("Voice Tuya cancellation gate : PASS")
        print()
        print(
            "Verify physically that Smart plug 2 "
            "remained OFF."
        )

    finally:
        await app.shutdown()


if __name__ == "__main__":
    asyncio.run(
        main()
    )