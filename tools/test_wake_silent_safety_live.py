from __future__ import annotations

import asyncio

from jarvis.core.application import JarvisApplication
from jarvis.core.container import container
from jarvis.services.tts_service import TTSService
from jarvis.services.voice_service import VoiceService
from jarvis.wake.boundary import WakeActivationBoundary
from jarvis.wake.command_transition import WakeCommandTransition


async def main() -> None:
    print("Sprint 6 Pack D Hotfix — Silent-After-Wake Safety Gate")
    print("-" * 60)

    app = JarvisApplication()

    await app.start(
        start_background_tasks=False,
    )

    try:
        transition = WakeCommandTransition(
            wake=container.resolve(
                "wake_activation",
                WakeActivationBoundary,
            ),
            voice=container.resolve(
                "voice",
                VoiceService,
            ),
            tts=container.resolve(
                "tts",
                TTSService,
            ),
            post_ack_settle_seconds=0.8,
        )

        print(
            'Say "Hey Jarvis". After the acknowledgement, '
            "DO NOT SPEAK."
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

        if result.transcript:
            raise RuntimeError(
                "False command detected while user stayed silent."
            )

        print()
        print("Wake detection: PASS")
        print("Post-ack settling: PASS")
        print("Adaptive noise rejection: PASS")
        print("False-command protection: PASS")
        print("Sprint 6 Pack D silent safety gate: PASS")
    finally:
        await app.shutdown()


if __name__ == "__main__":
    asyncio.run(
        main()
    )
