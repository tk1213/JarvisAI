from __future__ import annotations

import asyncio

from jarvis.core.application import JarvisApplication
from jarvis.core.container import container
from jarvis.memory.audit_service import MemoryAuditService
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
        audit = container.resolve(
            "memory_audit",
            MemoryAuditService,
        )

        await memory.remember(
            category=MemoryCategory.PERSONAL,
            key="audit_test_key",
            value="audit-test-value",
            importance=MemoryImportance.NORMAL,
            source="audit_live_test",
        )

        await memory.forget(
            "audit_test_key"
        )

        events = await audit.list_recent(
            limit=10
        )

        print()
        print("Recent memory audit events")
        print("-" * 60)

        for event in events:
            print(
                f"{event.created_at.isoformat()} "
                f"{event.action.value:<9} "
                f"{event.key} "
                f"value={event.value!r} "
                f"source={event.source!r} "
                f"reason={event.reason}"
            )

    finally:
        await app.shutdown()


if __name__ == "__main__":
    asyncio.run(
        main()
    )
