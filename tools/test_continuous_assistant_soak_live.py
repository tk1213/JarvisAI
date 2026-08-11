from __future__ import annotations

import asyncio
from dataclasses import dataclass

from jarvis.core.application import JarvisApplication
from jarvis.core.container import container
from jarvis.services.conversation_manager import ConversationManager
from jarvis.services.tts_service import TTSService
from jarvis.services.voice_service import VoiceService
from jarvis.wake.boundary import WakeActivationBoundary
from jarvis.wake.command_transition import WakeCommandTransition
from jarvis.wake.full_turn import WakeActivatedTurnRuntime


@dataclass(slots=True)
class SoakTurn:
    number: int
    transcript: str
    reply: str
    wake_score: float
    completed: bool


async def main() -> None:
    print("Sprint 6 Pack F Hotfix 4 — Reliability Soak Gate")
    print("-" * 60)
    print()
    print("This gate runs 10 wake-activated turns.")
    print()
    print("Suggested test sequence:")
    print("  1. วันนี้วันอะไร")
    print("  2. ทดสอบระบบ")
    print("  3. สวัสดี")
    print("  4. ตอนนี้กี่โมง")
    print("  5. SILENT TURN — say Hey Jarvis, then stay quiet")
    print("  6. เล่าเรื่องสั้นๆ")
    print("  7. Jarvis version")
    print("  8. เปิดสมาร์ทปลั๊ก")
    print("  9. วันนี้อากาศเป็นอย่างไร")
    print(" 10. ขอบคุณ")
    print()

    app = JarvisApplication()

    await app.start(
        start_background_tasks=False,
    )

    results: list[SoakTurn] = []

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

        runtime = WakeActivatedTurnRuntime(
            transition=transition,
            conversation=conversation,
            tts=tts,
        )

        for turn_number in range(1, 11):
            print()
            print("=" * 60)
            print(f"TURN {turn_number}/10")
            print('Say "Hey Jarvis", then speak the test phrase.')
            print("=" * 60)

            try:
                result = await runtime.run(
                    language="th",
                )

            except asyncio.CancelledError:
                print()
                print(
                    f"Turn {turn_number}: CANCELLED"
                )
                raise

            except Exception as exc:
                print()
                print(
                    f"Turn {turn_number}: ERROR"
                )
                print(
                    f"{type(exc).__name__}: {exc}"
                )
                raise

            completed = result.completed

            results.append(
                SoakTurn(
                    number=turn_number,
                    transcript=result.transcript,
                    reply=result.reply,
                    wake_score=result.wake_score,
                    completed=completed,
                )
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
            print(
                f"Completed  : {completed}"
            )

        print()
        print("=" * 60)
        print("SOAK SUMMARY")
        print("=" * 60)

        completed_count = sum(
            1
            for item in results
            if item.completed
        )

        empty_transcripts = sum(
            1
            for item in results
            if not item.transcript.strip()
        )

        print(
            f"Turns attempted : {len(results)}"
        )
        print(
            f"Completed turns : {completed_count}"
        )
        print(
            f"Empty transcript: {empty_transcripts}"
        )

        print()

        for item in results:
            status = (
                "PASS"
                if item.completed
                else "EMPTY/INCOMPLETE"
            )

            print(
                f"Turn {item.number:02d} | "
                f"wake={item.wake_score:.4f} | "
                f"{status} | "
                f"{item.transcript!r}"
            )

        print()

        if len(results) != 10:
            raise RuntimeError(
                "Soak gate did not finish all 10 turns."
            )

        print("10-turn runtime survival: PASS")
        print("Wake re-arm survival: PASS")
        print("No runtime crash: PASS")
        print("Sprint 6 Pack F Hotfix 4 soak gate: PASS")

    finally:
        await app.shutdown()


if __name__ == "__main__":
    asyncio.run(
        main()
    )