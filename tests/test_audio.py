from jarvis.audio.manager import AudioManager


def main() -> None:
    audio = AudioManager()
    audio.print_devices()


if __name__ == "__main__":
    main()