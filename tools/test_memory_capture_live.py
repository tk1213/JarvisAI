from __future__ import annotations

import asyncio

from jarvis.core.application import JarvisApplication
from jarvis.core.container import container
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

        print(
            'พิมพ์ใน "jarvis chat": ผมชื่อ TK'
        )
        print(
            "จากนั้นกลับมารันเครื่องมือนี้อีกครั้ง"
        )
        print()

        memories = await memory.list_memories()

        if not memories:
            print(
                "No long-term memories stored."
            )
            return

        for item in memories:
            print(
                f"[{item.category.value}] "
                f"{item.key} = {item.value}"
            )

    finally:
        await app.shutdown()


if __name__ == "__main__":
    asyncio.run(
        main()
    )
