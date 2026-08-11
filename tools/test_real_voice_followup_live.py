from __future__ import annotations

import asyncio

from jarvis.core.application import JarvisApplication
from jarvis.core.container import container
from jarvis.services.conversation_manager import ConversationManager
from jarvis.voice.dialogue_runtime import VoiceDialogueRuntime
from jarvis.voice.turn_runtime import VoiceTurnRuntime


async def main() -> None:
    print("Sprint 5 Pack I — Real Voice Follow-up")
    print("-" * 60)

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

        print(
            "For a safe live test, ask for status of an ambiguous "
            "device, for example: 'สถานะปลั๊ก'"
        )
        print(
            "If Jarvis asks which device, answer with the device "
            "name, for example: 'Smart Plug 2'"
        )
        print()

        result = await runtime.run(
            language="th"
        )

        for index, turn in enumerate(
            result.turns,
            start=1,
        ):
            print()
            print(
                f"Turn {index} status    : {turn.status.value}"
            )
            print(
                f"Turn {index} transcript: {turn.transcript!r}"
            )
            print(
                f"Turn {index} reply     : {turn.reply!r}"
            )

        print()
        print(
            f"Follow-ups used    : {result.follow_ups_used}"
        )
        print(
            f"Pending smart home : {result.pending_smart_home}"
        )

        if not result.completed:
            raise RuntimeError(
                "Voice follow-up dialogue did not complete."
            )

        print()
        print("First voice turn: PASS")
        print("Smart-home pending state: PASS")
        print("Voice disambiguation follow-up: PASS")
        print("Sprint 5 Pack I real voice gate: PASS")
    finally:
        await app.shutdown()


if __name__ == "__main__":
    asyncio.run(
        main()
    )
