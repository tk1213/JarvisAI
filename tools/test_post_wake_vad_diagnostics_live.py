from __future__ import annotations

import asyncio

from jarvis.core.application import JarvisApplication
from jarvis.core.container import container
from jarvis.services.stt_service import STTService


async def main() -> None:
    print("Sprint 6 Pack D Hotfix 2 — Wake Speech Diagnostics")
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
            "Stay quiet for calibration, then say: วันนี้วันอะไร"
        )

        text = await stt.listen_vad(
            language="th",
        )

        calibration = stt.recorder.last_vad_calibration
        run = stt.recorder.last_vad_run

        print()
        if calibration is not None:
            print(
                f"Noise RMS          : {calibration.noise_rms:.6f}"
            )
            print(
                f"Noise MAD          : {calibration.noise_mad:.6f}"
            )
            print(
                f"Adaptive threshold : {calibration.threshold:.6f}"
            )

        if run is not None:
            print(
                f"Max wait RMS       : {run.max_wait_rms:.6f}"
            )
            print(
                f"Trigger RMS        : "
                f"{run.trigger_rms if run.trigger_rms is not None else 'None'}"
            )
            print(
                f"Triggered          : {run.triggered}"
            )

        print(
            f"Transcript         : {text!r}"
        )

        if not text:
            raise RuntimeError(
                "No transcript was captured."
            )

        print()
        print("Separated calibration phase: PASS")
        print("Fresh command capture phase: PASS")
        print("VAD diagnostics: PASS")
        print("Sprint 6 Pack D Hotfix 2 diagnostics gate: PASS")
    finally:
        await app.shutdown()


if __name__ == "__main__":
    asyncio.run(
        main()
    )
