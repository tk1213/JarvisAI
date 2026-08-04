from __future__ import annotations

import queue
import time

import numpy as np
import sounddevice as sd
import soundfile as sf

from jarvis.audio.manager import AudioManager


def main() -> None:
    print("=" * 60)
    print(" JarvisAI - Callback Audio Quality Test")
    print("=" * 60)

    audio = AudioManager()

    sample_rate = audio.sample_rate
    duration = 3.0

    audio_queue: queue.Queue[np.ndarray] = queue.Queue()

    frames: list[np.ndarray] = []

    status_messages: list[str] = []

    def callback(
        indata: np.ndarray,
        frames_count: int,
        time_info: object,
        status: sd.CallbackFlags,
    ) -> None:
        del frames_count
        del time_info

        if status:
            status_messages.append(
                str(status)
            )

        audio_queue.put(
            indata.copy()
        )

    print()
    print(f"Input device : {audio.input_device}")
    print(f"Sample rate  : {sample_rate}")
    print("Block size   : native / automatic")
    print()
    print('พูด: "เปิดสมาร์ทปลั๊กสอง"')
    print()
    print("Recording...")

    with sd.InputStream(
        samplerate=sample_rate,
        blocksize=0,
        dtype="float32",
        channels=1,
        device=audio.input_device,
        latency="high",
        callback=callback,
    ):
        end_time = (
            time.monotonic()
            + duration
        )

        while time.monotonic() < end_time:
            try:
                frame = audio_queue.get(
                    timeout=0.1
                )
            except queue.Empty:
                continue

            frames.append(
                frame
            )

    while not audio_queue.empty():
        frames.append(
            audio_queue.get()
        )

    if not frames:
        raise RuntimeError(
            "No audio frames were captured."
        )

    recording = np.concatenate(
        frames,
        axis=0,
    )

    output = "callback_test.wav"

    sf.write(
        output,
        recording,
        sample_rate,
    )

    rms = float(
        np.sqrt(
            np.mean(
                np.square(recording)
            )
        )
    )

    peak = float(
        np.max(
            np.abs(recording)
        )
    )

    print("Recording finished.")
    print()
    print("=" * 60)
    print(" Result")
    print("=" * 60)
    print(f"File      : {output}")
    print(f"RMS       : {rms:.6f}")
    print(f"Peak      : {peak:.6f}")
    print(
        f"Warnings  : "
        f"{len(status_messages)}"
    )

    for message in status_messages:
        print(
            f" - {message}"
        )

    print("=" * 60)


if __name__ == "__main__":
    main()