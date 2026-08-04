from __future__ import annotations

import asyncio

from jarvis.core.application import JarvisApplication
from jarvis.core.container import container
from jarvis.memory.conflict import MemoryConflictPolicy
from jarvis.memory.service import MemoryService
from jarvis.memory.types import MemoryCategory, MemoryImportance


async def main() -> None:
    app = JarvisApplication()

    try:
        await app.start(start_background_tasks=False)

        memory = container.resolve(
            "long_term_memory",
            MemoryService,
        )

        await memory.remember(
            category=MemoryCategory.PERSONAL,
            key="user_name",
            value="TK",
            importance=MemoryImportance.HIGH,
            source="manual_test",
            conflict_policy=MemoryConflictPolicy.REPLACE,
        )

        await memory.remember(
            category=MemoryCategory.PERSONAL,
            key="user_name",
            value="SHOULD_NOT_REPLACE",
            importance=MemoryImportance.HIGH,
            source="manual_test",
            conflict_policy=MemoryConflictPolicy.KEEP_EXISTING,
        )

        current = await memory.recall("user_name")

        print(
            "Keep-existing policy: "
            f"{current.value if current else 'none'}"
        )

    finally:
        await app.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
