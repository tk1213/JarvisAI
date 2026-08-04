from __future__ import annotations

import time

import numpy as np
import sounddevice as sd
import soundfile as sf

from jarvis.audio.manager import AudioManager


def main() -> None:
    print("=" * 60)
    print(" JarvisAI - InputStream Audio Quality Test")
    print("=" * 60)

    audio = AudioManager()

    sample_rate = audio.sample_rate
    duration = 3.0
    frame_duration_ms = 20

    frame_samples = (
        sample_rate
        * frame_duration_ms
        // 1000
    )

    frames: list[np.ndarray] = []
    overflow_count = 0

    print()
    print(f"Input device : {audio.input_device}")
    print(f"Sample rate  : {sample_rate}")
    print(f"Frame size   : {frame_samples}")
    print()
    print('พูด: "เปิดสมาร์ทปลั๊กสอง"')
    print()
    print("Recording...")

    started_at = time.monotonic()

    with sd.InputStream(
        samplerate=sample_rate,
        blocksize=frame_samples,
        dtype="float32",
        channels=1,
        device=audio.input_device,
    ) as stream:
        while (
            time.monotonic()
            - started_at
            < duration
        ):
            frame, overflow = stream.read(
                frame_samples
            )

            if overflow:
                overflow_count += 1

            frames.append(
                np.asarray(
                    frame,
                    dtype=np.float32,
                ).copy()
            )

    recording = np.concatenate(
        frames,
        axis=0,
    )

    output = "inputstream_test.wav"

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
    print(f"Overflows : {overflow_count}")
    print("=" * 60)


if __name__ == "__main__":
    main()