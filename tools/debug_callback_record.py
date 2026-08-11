from __future__ import annotations

import queue
import time

import numpy as np
import sounddevice as sd
import soundfile as sf

DEVICE = 18
SAMPLE_RATE = 48000
CHANNELS = 1
SECONDS = 4.0

audio_queue: queue.Queue[np.ndarray] = queue.Queue()
frames: list[np.ndarray] = []


def callback(
    indata: np.ndarray,
    frame_count: int,
    time_info: object,
    status: sd.CallbackFlags,
) -> None:
    del frame_count
    del time_info

    if status:
        print(f"STATUS: {status}")

    audio_queue.put(
        np.asarray(
            indata,
            dtype=np.float32,
        ).copy()
    )


print("Raw callback InputStream recording test")
print("---------------------------------------")
print(f"Device     : {DEVICE}")
print(f"Sample rate: {SAMPLE_RATE}")
print()
print("Speak: วันนี้วันอะไร")
print()

with sd.InputStream(
    device=DEVICE,
    samplerate=SAMPLE_RATE,
    channels=CHANNELS,
    dtype="float32",
    blocksize=0,
    latency="high",
    callback=callback,
):
    deadline = time.monotonic() + SECONDS

    while time.monotonic() < deadline:
        try:
            frame = audio_queue.get(
                timeout=0.25
            )
        except queue.Empty:
            continue

        frames.append(
            frame
        )

if not frames:
    raise RuntimeError(
        "No callback audio frames were captured."
    )

audio = np.concatenate(
    frames,
    axis=0,
)

sf.write(
    "callback_test.wav",
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
        np.abs(
            audio
        )
    )
)

print(f"Frames   : {audio.shape[0]}")
print(
    f"Duration : "
    f"{audio.shape[0] / SAMPLE_RATE:.3f}"
)
print(f"RMS      : {rms:.6f}")
print(f"Peak     : {peak:.6f}")
print("Saved    : callback_test.wav")