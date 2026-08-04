from __future__ import annotations

import asyncio

from jarvis.core.application import JarvisApplication
from jarvis.core.container import container
from jarvis.memory.service import MemoryService
from jarvis.memory.types import (
    MemoryCategory,
    MemoryImportance,
)


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

        memory_id = await memory.remember(
            category=MemoryCategory.PERSONAL,
            key="user_name",
            value="TK",
            importance=MemoryImportance.HIGH,
            source="manual_repair",
        )

        print(
            f"user_name repaired: TK "
            f"(memory_id={memory_id})"
        )

    finally:
        await app.shutdown()


if __name__ == "__main__":
    asyncio.run(
        main()
    )
