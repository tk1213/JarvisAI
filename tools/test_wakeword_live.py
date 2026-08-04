from __future__ import annotations

import math
import queue

import numpy as np
import sounddevice as sd
from pyopen_wakeword import (
    Model,
    OpenWakeWord,
    OpenWakeWordFeatures,
)
from scipy.signal import resample_poly

from jarvis.audio.manager import AudioManager

WAKE_SAMPLE_RATE = 16000
WAKE_FRAME_SAMPLES = 160
WAKE_THRESHOLD = 0.50


def main() -> None:
    print("=" * 60)
    print(" JarvisAI - HEY_JARVIS Live Wake Word Test")
    print("=" * 60)
    print()

    audio = AudioManager()

    input_rate = audio.sample_rate

    print(f"Input device : {audio.input_device}")
    print(f"Input rate   : {input_rate}")
    print(f"Wake rate    : {WAKE_SAMPLE_RATE}")
    print(f"Threshold    : {WAKE_THRESHOLD:.2f}")
    print()

    print('พูดว่า: "Hey Jarvis"')
    print()
    print("Waiting for wake word...")
    print()

    features = OpenWakeWordFeatures.from_builtin()

    wake_word = OpenWakeWord.from_builtin(
        Model.HEY_JARVIS
    )

    audio_queue: queue.Queue[np.ndarray] = (
        queue.Queue()
    )

    status_messages: list[str] = []

    pcm_buffer = np.empty(
        0,
        dtype=np.int16,
    )

    best_score = 0.0

    gcd = math.gcd(
        input_rate,
        WAKE_SAMPLE_RATE,
    )

    up = WAKE_SAMPLE_RATE // gcd
    down = input_rate // gcd

    def callback(
        indata: np.ndarray,
        frames: int,
        time_info: object,
        status: sd.CallbackFlags,
    ) -> None:
        del frames
        del time_info

        if status:
            status_messages.append(
                str(status)
            )

        audio_queue.put(
            np.asarray(
                indata[:, 0],
                dtype=np.float32,
            ).copy()
        )

    try:
        with sd.InputStream(
            samplerate=input_rate,
            blocksize=0,
            dtype="float32",
            channels=1,
            device=audio.input_device,
            latency="high",
            callback=callback,
        ):
            while True:
                try:
                    native_chunk = audio_queue.get(
                        timeout=0.5
                    )
                except queue.Empty:
                    continue

                resampled = resample_poly(
                    native_chunk,
                    up=up,
                    down=down,
                )

                resampled = np.asarray(
                    resampled,
                    dtype=np.float32,
                )

                resampled = np.clip(
                    resampled,
                    -1.0,
                    1.0,
                )

                pcm16 = (
                    resampled
                    * 32767.0
                ).astype(
                    np.int16
                )

                pcm_buffer = np.concatenate(
                    (
                        pcm_buffer,
                        pcm16,
                    )
                )

                while (
                    len(pcm_buffer)
                    >= WAKE_FRAME_SAMPLES
                ):
                    frame = pcm_buffer[
                        :WAKE_FRAME_SAMPLES
                    ]

                    pcm_buffer = pcm_buffer[
                        WAKE_FRAME_SAMPLES:
                    ]

                    embeddings_iter = (
                        features.process_streaming(
                            frame.tobytes()
                        )
                    )

                    for embeddings in embeddings_iter:
                        scores = (
                            wake_word.process_streaming(
                                embeddings
                            )
                        )

                        for score in scores:
                            current_score = float(
                                score
                            )

                            if current_score > best_score:
                                best_score = current_score

                                print(
                                    "Wake score: "
                                    f"{best_score:.4f}"
                                )

                            if (
                                current_score
                                >= WAKE_THRESHOLD
                            ):
                                print()
                                print("=" * 60)
                                print(
                                    " HEY JARVIS DETECTED"
                                )
                                print("=" * 60)
                                print(
                                    f"Score: "
                                    f"{current_score:.4f}"
                                )

                                if status_messages:
                                    print(
                                        "Audio warnings: "
                                        f"{len(status_messages)}"
                                    )

                                return

    except KeyboardInterrupt:
        print()
        print("Wake word test stopped by user.")

    finally:
        features.close()
        wake_word.close()

        print()
        print(
            f"Best wake score: "
            f"{best_score:.4f}"
        )


if __name__ == "__main__":
    main()