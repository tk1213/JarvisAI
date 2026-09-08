from __future__ import annotations

import argparse
import asyncio

from jarvis.audio.manager import AudioManager
from jarvis.config.audio_device_config import AudioDeviceConfig
from jarvis.main import audio_devices, chat, doctor, run
from jarvis.version import __version__


def set_audio_input_device(
    device_index: int,
) -> None:
    audio = AudioManager()
    selected = audio.select_input(
        device_index,
    )

    AudioDeviceConfig().set_input_device(
        selected.index,
        name=selected.name,
        host_api=selected.host_api,
    )

    print(
        "Audio input device saved: "
        f"[{selected.index}] {selected.name}"
    )


def set_audio_output_device(
    device_index: int,
) -> None:
    audio = AudioManager()
    selected = audio.select_output(
        device_index,
    )

    AudioDeviceConfig().set_output_device(
        selected.index,
        name=selected.name,
        host_api=selected.host_api,
    )

    print(
        "Audio output device saved: "
        f"[{selected.index}] {selected.name}"
    )


def reset_audio_devices() -> None:
    config = AudioDeviceConfig()
    config.reset_input_device()
    config.reset_output_device()

    print(
        "Audio device selection reset "
        "to automatic."
    )


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="jarvis",
        description="JarvisAI command-line interface",
    )

    subparsers = parser.add_subparsers(
        dest="command",
    )

    subparsers.add_parser(
        "run",
        help="Start JarvisAI",
    )

    subparsers.add_parser(
        "chat",
        help="Chat with JarvisAI",
    )

    subparsers.add_parser(
        "doctor",
        help="Check JarvisAI system health",
    )

    audio_parser = subparsers.add_parser(
        "audio",
        help="List or configure audio devices",
    )

    audio_subparsers = audio_parser.add_subparsers(
        dest="audio_command",
    )

    input_parser = audio_subparsers.add_parser(
        "input",
        help="Select the persistent input device",
    )
    input_parser.add_argument(
        "device_index",
        type=int,
        help="Audio input device index",
    )

    output_parser = audio_subparsers.add_parser(
        "output",
        help="Select the persistent output device",
    )
    output_parser.add_argument(
        "device_index",
        type=int,
        help="Audio output device index",
    )

    audio_subparsers.add_parser(
        "reset",
        help="Reset input and output to automatic",
    )

    subparsers.add_parser(
        "version",
        help="Show JarvisAI version",
    )

    return parser


def main() -> None:
    parser = create_parser()
    args = parser.parse_args()

    command = args.command or "run"

    try:
        if command == "run":
            asyncio.run(run())

        elif command == "chat":
            asyncio.run(chat())

        elif command == "doctor":
            healthy = asyncio.run(doctor())

            if not healthy:
                raise SystemExit(1)

        elif command == "audio":
            audio_command = args.audio_command

            if audio_command == "input":
                set_audio_input_device(
                    args.device_index,
                )

            elif audio_command == "output":
                set_audio_output_device(
                    args.device_index,
                )

            elif audio_command == "reset":
                reset_audio_devices()

            else:
                asyncio.run(audio_devices())

        elif command == "version":
            print(f"JarvisAI {__version__}")

        else:
            parser.print_help()

    except KeyboardInterrupt:
        print()
        print("JarvisAI stopped by user.")


if __name__ == "__main__":
    main()