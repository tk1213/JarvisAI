from pathlib import Path

import sounddevice as sd
import soundfile as sf

from jarvis.audio.manager import AudioManager


class AudioRecorder:
    def __init__(self) -> None:
        self.audio = AudioManager()

    def record(
        self,
        seconds: float = 5.0,
        output: str = "record.wav",
    ) -> Path:
        output_path = Path(output).resolve()

        print(f"Recording {seconds:.1f} seconds...")

        recording = sd.rec(
            int(seconds * self.audio.sample_rate),
            samplerate=self.audio.sample_rate,
            channels=self.audio.channels,
            dtype="float32",
            device=self.audio.input_device,
        )

        sd.wait()

        sf.write(
            output_path,
            recording,
            self.audio.sample_rate,
        )

        print("Recording finished.")

        return output_path