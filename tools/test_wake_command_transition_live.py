from __future__ import annotations

import asyncio

from jarvis.core.application import JarvisApplication
from jarvis.core.container import container
from jarvis.services.tts_service import TTSService
from jarvis.services.voice_service import VoiceService
from jarvis.wake.boundary import WakeActivationBoundary
from jarvis.wake.command_transition import WakeCommandTransition


async def main() -> None:
    print("Sprint 6 Pack D — Wake -> Acknowledge -> Spoken Command")
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

        transition = WakeCommandTransition(
            wake=wake,
            voice=voice,
            tts=tts,
        )

        print(
            'Say "Hey Jarvis". '
            "After Jarvis acknowledges, speak one clear Thai command."
        )
        print()

        result = await transition.run(
            language="th"
        )

        print()
        print(
            f"Wake score : {result.wake_score:.4f}"
        )
        print(
            f"Transcript : {result.transcript!r}"
        )

        if not result.completed:
            raise RuntimeError(
                "No command was captured after wake acknowledgement."
            )

        print()
        print("Wake detection: PASS")
        print("Acknowledgement playback: PASS")
        print("Post-wake command capture: PASS")
        print("Sprint 6 Pack D hardware live gate: PASS")
    finally:
        await app.shutdown()


if __name__ == "__main__":
    asyncio.run(
        main()
    )
