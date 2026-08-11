from __future__ import annotations

import asyncio

from jarvis.audio.manager import AudioManager
from jarvis.services.wake_word_service import WakeWordService
from jarvis.wake.boundary import WakeActivationBoundary


async def main() -> None:
    audio = AudioManager()

    wake_word = WakeWordService(
        audio=audio,
        threshold=0.50,
    )

    print("Sprint 6 Pack B — Real Wake Word Hardware Detection")
    print("-" * 60)
    print(
        f"Input device: [{audio.input_device}] "
        f"{audio.input_info.name}"
    )
    print(
        f"Input sample rate: "
        f"{audio.input_info.default_sample_rate} Hz"
    )
    print(
        f"Wake model: {wake_word.model_name}"
    )
    print(
        f"Threshold: {wake_word.threshold:.2f}"
    )
    print()
    print(
        'Say "Hey Jarvis" clearly within 20 seconds...'
    )

    try:
        result = await asyncio.wait_for(
            WakeActivationBoundary(
                wake_word
            ).wait(),
            timeout=20.0,
        )

    except TimeoutError as exc:
        raise RuntimeError(
            "Wake word was not detected within 20 seconds."
        ) from exc

    finally:
        wake_word.close()

    if not result.detected:
        raise RuntimeError(
            f"Wake activation ended with status: "
            f"{result.status.value}"
        )

    print()
    print(
        f"Detected score: {result.score:.4f}"
    )
    print("Shared AudioManager: PASS")
    print("Real microphone stream: PASS")
    print("Wake-word model activation: PASS")
    print("Wake activation boundary: PASS")
    print("Sprint 6 Pack B hardware live gate: PASS")


if __name__ == "__main__":
    asyncio.run(
        main()
    )
