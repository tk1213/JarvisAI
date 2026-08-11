from __future__ import annotations

import asyncio

from jarvis.core.application import JarvisApplication
from jarvis.core.container import container
from jarvis.services.conversation_manager import ConversationManager
from jarvis.services.tts_service import TTSService
from jarvis.services.voice_service import VoiceService
from jarvis.wake.boundary import WakeActivationBoundary
from jarvis.wake.command_transition import WakeCommandTransition
from jarvis.wake.full_turn import (
    WakeActivatedTurnResult,
    WakeActivatedTurnRuntime,
)


def print_turn_result(
    *,
    number: int,
    result: WakeActivatedTurnResult,
) -> None:
    print()
    print("-" * 60)
    print(f"TURN {number} RESULT")
    print("-" * 60)
    print(
        f"Wake score : {result.wake_score:.4f}"
    )
    print(
        f"Transcript : {result.transcript!r}"
    )
    print(
        f"Reply      : {result.reply!r}"
    )
    print(
        f"Completed  : {result.completed}"
    )


async def main() -> None:
    print(
        "Sprint 6 Pack G4.10.7 — "
        "Continuous Re-arm Silent Recovery Gate"
    )
    print("-" * 60)

    app = JarvisApplication()

    await app.start(
        start_background_tasks=False,
    )

    try:
        wake = container.resolve(
            "wake_activation",
            WakeActivationBoundary,
        )
        voice = container.resolve(
            "voice",
            VoiceService,
        )
        tts = container.resolve(
            "tts",
            TTSService,
        )
        conversation = container.resolve(
            "conversation",
            ConversationManager,
        )

        transition = WakeCommandTransition(
            wake=wake,
            voice=voice,
            tts=tts,
            post_ack_settle_seconds=0.25,
        )

        turn_runtime = WakeActivatedTurnRuntime(
            transition=transition,
            conversation=conversation,
            tts=tts,
        )

        print()
        print("=" * 60)
        print("TURN 1 — SILENT COMMAND")
        print("=" * 60)
        print()
        print('Say "Hey Jarvis".')
        print(
            "After acknowledgement, remain silent."
        )
        print(
            "Wait until Jarvis finishes the silent turn."
        )
        print()

        first = await turn_runtime.run(
            language="th",
        )

        print_turn_result(
            number=1,
            result=first,
        )

        if first.transcript:
            raise RuntimeError(
                "Turn 1 was expected to be silent, "
                f"but transcript was {first.transcript!r}."
            )

        if first.reply:
            raise RuntimeError(
                "Silent Turn 1 unexpectedly produced "
                f"a reply: {first.reply!r}."
            )

        print()
        print("Silent turn rejection: PASS")

        print()
        print("=" * 60)
        print("TURN 2 — WAKE RE-ARM")
        print("=" * 60)
        print()
        print(
            "Turn 1 is complete."
        )
        print(
            'NOW say "Hey Jarvis" again.'
        )
        print(
            'After acknowledgement, say "วันนี้วันอะไร".'
        )
        print()

        second = await turn_runtime.run(
            language="th",
        )

        print_turn_result(
            number=2,
            result=second,
        )

        if not second.transcript:
            raise RuntimeError(
                "Turn 2 captured no transcript "
                "after wake re-arm."
            )

        if not second.reply:
            raise RuntimeError(
                "Turn 2 produced no reply "
                "after wake re-arm."
            )

        if not second.completed:
            raise RuntimeError(
                "Turn 2 did not complete successfully."
            )

        print()
        print("=" * 60)
        print("G4.10.7 SILENT RECOVERY RESULT")
        print("=" * 60)
        print()
        print("Silent turn rejection: PASS")
        print("Wake re-arm after silence: PASS")
        print("Second wake activation: PASS")
        print("Next real turn completion: PASS")
        print("No cancellation leakage: PASS")
        print(
            "Sprint 6 Pack G4.10.7 "
            "silent recovery gate: PASS"
        )

    finally:
        await app.shutdown()


if __name__ == "__main__":
    asyncio.run(
        main()
    )