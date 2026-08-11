from __future__ import annotations

import asyncio

from jarvis.core.application import JarvisApplication
from jarvis.core.container import container
from jarvis.services.conversation_manager import ConversationManager
from jarvis.services.stt_service import STTService
from jarvis.services.tts_service import TTSService
from jarvis.services.voice_service import VoiceService
from jarvis.wake.boundary import WakeActivationBoundary
from jarvis.wake.command_transition import WakeCommandTransition
from jarvis.wake.full_turn import WakeActivatedTurnRuntime


def format_seconds(
    value: float | None,
) -> str:
    if value is None:
        return "n/a"

    return f"{value:.3f} s"


async def main() -> None:
    print(
        "Sprint 6 Pack G4.9.3 — "
        "Detailed Wake Latency Live Gate"
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

        stt = container.resolve(
            "stt",
            STTService,
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
            acknowledgement="ครับ TK",
            post_ack_settle_seconds=0.25,
        )

        runtime = WakeActivatedTurnRuntime(
            transition=transition,
            conversation=conversation,
            tts=tts,
        )

        print()
        print(
            'Say "Hey Jarvis". '
            'After acknowledgement, '
            'say "เย็นนี้กินอะไรดี".'
        )
        print()

        result = await runtime.run(
            language="th",
        )

        print()
        print(
            f"Wake score : "
            f"{result.wake_score:.4f}"
        )
        print(
            f"Transcript : "
            f"{result.transcript!r}"
        )
        print(
            f"Reply      : "
            f"{result.reply!r}"
        )

        timing = result.timing

        if timing is None:
            raise RuntimeError(
                "TurnTiming was not attached "
                "to the turn result."
            )

        print()
        print("Latency report")
        print("-" * 60)

        print(
            "Wake wait        : "
            f"{format_seconds(timing.wake_seconds)}"
        )

        print(
            "Acknowledgement  : "
            f"{format_seconds(timing.acknowledgement_seconds)}"
        )

        print(
            "Command capture  : "
            f"{format_seconds(timing.command_capture_seconds)}"
        )

        print(
            "Post-ACK settle  : "
            f"{format_seconds(timing.post_ack_seconds)}"
        )

        print(
            "Command listen   : "
            f"{format_seconds(timing.command_listen_seconds)}"
        )

        stt_timing = stt.last_timing

        if stt_timing is not None:
            print(
                "  Calibration   : "
                f"{format_seconds(stt_timing.calibration_seconds)}"
            )

            print(
                "  Speech/VAD    : "
                f"{format_seconds(stt_timing.capture_seconds)}"
            )

            print(
                "  Signal check  : "
                f"{format_seconds(stt_timing.diagnostics_seconds)}"
            )

            print(
                "  16k normalize : "
                f"{format_seconds(stt_timing.normalization_seconds)}"
            )

            print(
                "  STT API       : "
                f"{format_seconds(stt_timing.transcription_seconds)}"
            )

            print(
                "  STT total     : "
                f"{format_seconds(stt_timing.total_seconds)}"
            )

        print(
            "Conversation/AI  : "
            f"{format_seconds(timing.conversation_seconds)}"
        )

        print(
            "Reply TTS        : "
            f"{format_seconds(timing.tts_seconds)}"
        )

        tts_timing = tts.last_timing

        if tts_timing is not None:
            print(
                "  Generation     : "
                f"{format_seconds(tts_timing.generation_seconds)}"
            )

            print(
                "  Player prepare : "
                f"{format_seconds(tts_timing.player_preparation_seconds)}"
            )

            print(
                "  First audio    : "
                f"{format_seconds(tts_timing.time_to_first_audio_seconds)}"
            )

            print(
                "  Playback       : "
                f"{format_seconds(tts_timing.playback_seconds)}"
            )

            print(
                "  TTS total      : "
                f"{format_seconds(tts_timing.total_seconds)}"
            )

        print("-" * 60)

        print(
            "Total            : "
            f"{format_seconds(timing.total_seconds)}"
        )

        if not result.transcript:
            raise RuntimeError(
                "No transcript was captured."
            )

        if not result.reply:
            raise RuntimeError(
                "No reply was produced."
            )

        print()
        print(
            "Timing instrumentation: PASS"
        )
        print(
            "Wake -> STT timing: PASS"
        )
        print(
            "Conversation timing: PASS"
        )
        print(
            "TTS timing: PASS"
        )
        print(
            "Sprint 6 Pack G4.9.3 "
            "latency gate: PASS"
        )

    finally:
        await app.shutdown()


if __name__ == "__main__":
    asyncio.run(
        main()
    )