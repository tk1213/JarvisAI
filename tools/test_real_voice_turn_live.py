from __future__ import annotations

import asyncio

from jarvis.core.application import JarvisApplication
from jarvis.core.container import container
from jarvis.voice.turn_runtime import (
    VoiceTurnRuntime,
    VoiceTurnStatus,
)


async def main() -> None:
    print("Sprint 5 Pack H — Real End-to-End Spoken Jarvis Turn")
    print("-" * 60)

    app = JarvisApplication()

    await app.start(
        start_background_tasks=False,
    )

    try:
        runtime = container.resolve(
            "voice_turn",
            VoiceTurnRuntime,
        )

        print(
            "Wait briefly, speak a clear Thai sentence, "
            "then stop speaking..."
        )

        result = await runtime.run(
            language="th"
        )

        print()
        print(
            f"Status    : {result.status.value}"
        )
        print(
            f"Transcript: {result.transcript!r}"
        )
        print(
            f"Reply     : {result.reply!r}"
        )

        if result.status is not VoiceTurnStatus.COMPLETED:
            raise RuntimeError(
                "Voice turn did not complete: "
                f"{result.status.value}"
            )

        print()
        print("Application lifecycle: PASS")
        print("VAD -> STT: PASS")
        print("ConversationManager: PASS")
        print("TTS generation/playback: PASS")
        print("Sprint 5 Pack H real voice gate: PASS")
    finally:
        await app.shutdown()


if __name__ == "__main__":
    asyncio.run(
        main()
    )
