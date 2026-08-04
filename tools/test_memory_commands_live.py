from __future__ import annotations

import asyncio

from jarvis.core.application import JarvisApplication
from jarvis.core.container import container
from jarvis.memory.commands import MemoryCommandService


async def main() -> None:
    app = JarvisApplication()

    try:
        await app.start(
            start_background_tasks=False,
        )

        commands = container.resolve(
            "memory_commands",
            MemoryCommandService,
        )

        tests = (
            "What do you remember about me?",
            "Forget my favorite drink",
        )

        for text in tests:
            print()
            print(f"You: {text}")
            reply = await commands.handle(
                text
            )
            print(
                f"Jarvis: {reply}"
            )

            if commands.has_pending_confirmation:
                cancel_reply = await commands.handle(
                    "cancel"
                )
                print(
                    f"Jarvis: {cancel_reply}"
                )

    finally:
        await app.shutdown()


if __name__ == "__main__":
    asyncio.run(
        main()
    )
