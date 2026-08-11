from __future__ import annotations

import asyncio
from pathlib import Path

from jarvis.audio.manager import AudioManager
from jarvis.audio.recorder import AudioRecorder
from jarvis.audio.signal_diagnostics import AudioSignalAnalyzer
from jarvis.services.stt_service import STTService
from jarvis.speech.stt import SpeechToText


async def main() -> None:
    manager = AudioManager()
    recorder = AudioRecorder(
        manager
    )
    analyzer = AudioSignalAnalyzer()
    stt = SpeechToText()

    service = STTService(
        recorder=recorder,
        stt=stt,
        signal_analyzer=analyzer,
    )

    output = Path(
        "tmp/audio/sprint5_pack_e_stt.wav"
    )

    print("Sprint 5 Pack E — Production Microphone -> STT Integration")
    print("-" * 60)
    print(
        f"Input device: [{manager.input_device}] "
        f"{manager.input_info.name}"
    )
    print(
        "Recording 5 seconds. Speak a clear Thai sentence now..."
    )

    text = await service.listen_fixed(
        seconds=5.0,
        language="th",
        output=str(
            output
        ),
    )

    signal = service.last_signal

    if signal is None:
        raise RuntimeError(
            "Signal diagnostics were not produced."
        )

    print()
    print(
        f"Signal status: {signal.status.value}"
    )
    print(
        f"RMS: {signal.rms:.6f}"
    )
    print(
        f"Peak: {signal.peak:.6f}"
    )
    print(
        f"Transcript: {text!r}"
    )

    if not signal.usable_for_stt:
        raise RuntimeError(
            "Recorded audio is not usable for STT."
        )

    if not text:
        raise RuntimeError(
            "STT returned an empty transcript."
        )

    print("Microphone capture: PASS")
    print("Signal validation: PASS")
    print("OpenAI STT transcription: PASS")
    print("Sprint 5 Pack E live gate: PASS")


if __name__ == "__main__":
    asyncio.run(
        main()
    )
