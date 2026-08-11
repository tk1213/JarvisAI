from __future__ import annotations

from jarvis.audio.manager import AudioManager
from jarvis.audio.player import AudioPlayer
from jarvis.audio.recorder import AudioRecorder


def main() -> None:
    audio = AudioManager()
    recorder = AudioRecorder(
        audio=audio
    )
    player = AudioPlayer(
        audio=audio
    )

    assert recorder._audio is audio
    assert player.audio is audio

    print("Sprint 5 Pack H — Production Voice Wiring")
    print("-" * 60)
    print(
        f"Input : [{audio.input_device}] "
        f"{audio.input_info.name}"
    )
    print(
        f"Output: [{audio.output_device}] "
        f"{audio.output_info.name}"
    )
    print("Shared AudioManager: PASS")
    print("Recorder wiring: PASS")
    print("Player wiring: PASS")
    print("Sprint 5 Pack H live gate: PASS")


if __name__ == "__main__":
    main()
