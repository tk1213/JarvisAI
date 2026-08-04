import argparse
import asyncio

from jarvis.main import chat, doctor, run
from jarvis.version import __version__


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

        elif command == "version":
            print(f"JarvisAI {__version__}")

        else:
            parser.print_help()

    except KeyboardInterrupt:
        print()
        print("JarvisAI stopped by user.")


if __name__ == "__main__":
    main()