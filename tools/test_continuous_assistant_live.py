from __future__ import annotations

import asyncio

from jarvis.core.application import JarvisApplication
from jarvis.core.container import container
from jarvis.services.conversation_manager import ConversationManager
from jarvis.services.tts_service import TTSService
from jarvis.services.voice_service import VoiceService
from jarvis.wake.boundary import WakeActivationBoundary
from jarvis.wake.command_transition import WakeCommandTransition
from jarvis.wake.continuous_runtime import ContinuousAssistantRuntime
from jarvis.wake.full_turn import WakeActivatedTurnRuntime


async def main() -> None:
    print("Sprint 6 Pack F — Bounded Continuous Assistant Runtime")
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
            post_ack_settle_seconds=0.8,
        )

        turn_runtime = WakeActivatedTurnRuntime(
            transition=transition,
            conversation=conversation,
            tts=tts,
        )

        runtime = ContinuousAssistantRuntime(
            turn_runtime=turn_runtime,
        )

        print(
            "This live gate will run exactly 2 wake-activated turns."
        )
        print()
        print(
            'Turn 1: say "Hey Jarvis", then ask "วันนี้วันอะไร".'
        )
        print(
            'Turn 2: say "Hey Jarvis", then say "ทดสอบระบบ".'
        )
        print()

        result = await runtime.run(
            language="th",
            max_turns=2,
        )

        print()
        print(
            f"Stop reason    : {result.stop_reason}"
        )
        print(
            f"Turns captured : {len(result.turns)}"
        )
        print(
            f"Completed turns: {result.completed_turns}"
        )

        for index, turn in enumerate(
            result.turns,
            start=1,
        ):
            print()
            print(
                f"Turn {index} wake score : "
                f"{turn.wake_score:.4f}"
            )
            print(
                f"Turn {index} transcript : "
                f"{turn.transcript!r}"
            )
            print(
                f"Turn {index} reply      : "
                f"{turn.reply!r}"
            )

        if len(result.turns) != 2:
            raise RuntimeError(
                "Continuous runtime did not complete two bounded turns."
            )

        if result.completed_turns != 2:
            raise RuntimeError(
                "One or more wake-activated turns did not complete."
            )

        print()
        print("Wake re-arm after first turn: PASS")
        print("Second wake-activated turn: PASS")
        print("Bounded stop after max turns: PASS")
        print("Sprint 6 Pack F live gate: PASS")
    finally:
        await app.shutdown()


if __name__ == "__main__":
    asyncio.run(
        main()
    )
