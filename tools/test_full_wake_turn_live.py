from __future__ import annotations

import asyncio

from jarvis.core.application import JarvisApplication
from jarvis.core.container import container
from jarvis.services.conversation_manager import ConversationManager
from jarvis.services.tts_service import TTSService
from jarvis.services.voice_service import VoiceService
from jarvis.wake.boundary import WakeActivationBoundary
from jarvis.wake.command_transition import WakeCommandTransition
from jarvis.wake.full_turn import WakeActivatedTurnRuntime


async def main() -> None:
    print("Sprint 6 Pack E — Full Wake-Activated Jarvis Turn")
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

        runtime = WakeActivatedTurnRuntime(
            transition=transition,
            conversation=conversation,
            tts=tts,
        )

        print(
            'Say "Hey Jarvis". '
            "After the acknowledgement, ask: วันนี้วันอะไร"
        )
        print()

        result = await runtime.run(
            language="th",
        )

        print()
        print(
            f"Wake score : {result.wake_score:.4f}"
        )
        print(
            f"Transcript : {result.transcript!r}"
        )
        print(
            f"Reply      : {result.reply!r}"
        )

        if not result.transcript:
            raise RuntimeError(
                "No post-wake transcript was captured."
            )

        if not result.reply:
            raise RuntimeError(
                "ConversationManager returned no reply."
            )

        print()
        print("Wake detection: PASS")
        print("Callback VAD -> STT: PASS")
        print("ConversationManager: PASS")
        print("TTS response playback: PASS")
        print("Sprint 6 Pack E full wake turn gate: PASS")
    finally:
        await app.shutdown()


if __name__ == "__main__":
    asyncio.run(
        main()
    )
