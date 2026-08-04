from __future__ import annotations

import asyncio

from jarvis.core.application import JarvisApplication
from jarvis.core.container import container
from jarvis.memory.retriever import MemoryRetriever


async def main() -> None:
    app = JarvisApplication()

    try:
        await app.start(
            start_background_tasks=False,
        )

        retriever = container.resolve(
            "memory_retriever",
            MemoryRetriever,
        )

        queries = (
            "What is my name?",
            "What is my favorite drink?",
            "What is the weather today?",
        )

        for query in queries:
            print()
            print(f"Query: {query}")

            memories = await retriever.retrieve(
                query
            )

            if not memories:
                print(
                    "Relevant memories: none"
                )
                continue

            print(
                "Relevant memories:"
            )

            for memory in memories:
                print(
                    f"- {memory.key} = "
                    f"{memory.value}"
                )

    finally:
        await app.shutdown()


if __name__ == "__main__":
    asyncio.run(
        main()
    )
