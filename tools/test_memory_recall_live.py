from __future__ import annotations

import asyncio

from jarvis.core.application import JarvisApplication
from jarvis.core.container import container
from jarvis.memory.context import MemoryContextBuilder
from jarvis.memory.service import MemoryService


async def main() -> None:
    app = JarvisApplication()

    try:
        await app.start(
            start_background_tasks=False,
        )

        memory = container.resolve(
            "long_term_memory",
            MemoryService,
        )
        builder = container.resolve(
            "memory_context",
            MemoryContextBuilder,
        )

        memories = await memory.list_memories(
            limit=20,
        )

        print("Stored long-term memories")
        print("-" * 40)

        for item in memories:
            print(
                f"[{item.category.value}] "
                f"{item.key} = {item.value}"
            )

        print()
        print("Generated memory context")
        print("-" * 40)

        print(
            await builder.build(
                "What is my name?"
            )
        )

    finally:
        await app.shutdown()


if __name__ == "__main__":
    asyncio.run(
        main()
    )
