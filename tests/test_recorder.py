from jarvis.audio.recorder import AudioRecorder


def main() -> None:
    recorder = AudioRecorder()

    audio = recorder.record(
        seconds=5,
        output="record.wav",
    )

    print(audio)


if __name__ == "__main__":
    main()