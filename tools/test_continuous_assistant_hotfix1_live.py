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
    print("Sprint 6 Pack F Hotfix 1 — Wake Handoff Diagnostics")
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
            acknowledgement="ครับ คุณ TK",
            post_ack_settle_seconds=0.25,
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
            "This gate runs exactly 2 wake-activated turns."
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
            f"Stop reason       : {result.stop_reason}"
        )
        print(
            f"Cancellation stage: {result.cancellation_stage}"
        )
        print(
            f"Turns captured    : {len(result.turns)}"
        )
        print(
            f"Completed turns   : {result.completed_turns}"
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

        if result.stop_reason == "cancelled":
            raise RuntimeError(
                "Continuous runtime was cancelled at "
                f"{result.cancellation_stage}."
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
        print("Short post-ack handoff: PASS")
        print("Wake re-arm: PASS")
        print("Two bounded turns: PASS")
        print("Sprint 6 Pack F Hotfix 1 live gate: PASS")
    finally:
        await app.shutdown()


if __name__ == "__main__":
    asyncio.run(
        main()
    )
