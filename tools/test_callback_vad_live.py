from __future__ import annotations

import asyncio

from jarvis.core.application import JarvisApplication
from jarvis.core.container import container
from jarvis.services.stt_service import STTService


async def main() -> None:
    print("Sprint 6 Pack D Hotfix 3 — Callback VAD Live Gate")
    print("-" * 60)

    app = JarvisApplication()

    await app.start(
        start_background_tasks=False,
    )

    try:
        stt = container.resolve(
            "stt",
            STTService,
        )

        print(
            "Stay quiet briefly, then say: วันนี้วันอะไร"
        )
        print()

        text = await stt.listen_vad(
            language="th",
            output="callback_vad.wav",
        )

        calibration = stt.recorder.last_vad_calibration
        run = stt.recorder.last_vad_run

        print()

        if calibration is not None:
            print(
                f"Noise RMS          : "
                f"{calibration.noise_rms:.6f}"
            )
            print(
                f"Adaptive threshold : "
                f"{calibration.threshold:.6f}"
            )

        if run is not None:
            print(
                f"Max wait RMS       : "
                f"{run.max_wait_rms:.6f}"
            )
            print(
                f"Trigger RMS        : "
                f"{run.trigger_rms}"
            )
            print(
                f"Triggered          : "
                f"{run.triggered}"
            )

        print(
            f"Transcript         : {text!r}"
        )

        if not text:
            raise RuntimeError(
                "Callback VAD produced no transcript."
            )

        print()
        print("Callback microphone capture: PASS")
        print("VAD trigger: PASS")
        print("WAV persistence: PASS")
        print("STT transcription: PASS")
        print("Sprint 6 Pack D Hotfix 3 live gate: PASS")
    finally:
        await app.shutdown()


if __name__ == "__main__":
    asyncio.run(
        main()
    )
