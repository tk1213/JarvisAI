from __future__ import annotations

import time

import numpy as np
import sounddevice as sd
import soundfile as sf

DEVICE = 18
SAMPLE_RATE = 48000
CHANNELS = 1
BLOCKSIZE = 960
SECONDS = 4

print("Raw InputStream recording test")
print("--------------------------------")
print(f"Device     : {DEVICE}")
print(f"Sample rate: {SAMPLE_RATE}")
print(f"Block size : {BLOCKSIZE}")
print()
print("Speak: วันนี้วันอะไร")
print()

frames: list[np.ndarray] = []

with sd.InputStream(
    device=DEVICE,
    samplerate=SAMPLE_RATE,
    channels=CHANNELS,
    dtype="float32",
    blocksize=BLOCKSIZE,
) as stream:
    start = time.monotonic()

    while time.monotonic() - start < SECONDS:
        data, overflowed = stream.read(
            BLOCKSIZE
        )

        if overflowed:
            print("WARNING: input overflow")

        frames.append(
            np.asarray(
                data,
                dtype=np.float32,
            ).copy()
        )

audio = np.concatenate(
    frames,
    axis=0,
)

sf.write(
    "inputstream_test.wav",
    audio,
    SAMPLE_RATE,
)

rms = float(
    np.sqrt(
        np.mean(
            np.square(
                audio,
                dtype=np.float64,
            )
        )
    )
)

peak = float(
    np.max(
        np.abs(audio)
    )
)

print()
print(f"Frames   : {audio.shape[0]}")
print(f"Duration : {audio.shape[0] / SAMPLE_RATE:.3f}")
print(f"RMS      : {rms:.6f}")
print(f"Peak     : {peak:.6f}")
print("Saved    : inputstream_test.wav")