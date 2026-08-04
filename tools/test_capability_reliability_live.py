from __future__ import annotations

import asyncio

from jarvis.core.application import JarvisApplication
from jarvis.core.container import container
from jarvis.planner.capability_reliability import (
    CapabilityReliabilityService,
)
from jarvis.planner.capability_reliability_report import (
    CapabilityReliabilityReportBuilder,
)
from jarvis.planner.execution_persistence import (
    ExecutionPersistenceService,
)


async def main() -> None:
    app = JarvisApplication()

    try:
        await app.start(
            start_background_tasks=False,
        )

        persistence = container.resolve(
            "execution_persistence",
            ExecutionPersistenceService,
        )

        service = CapabilityReliabilityService(
            persistence
        )

        reliability = await service.summarize(
            limit=100
        )

        report = CapabilityReliabilityReportBuilder().build(
            reliability
        )

        print(
            "Sprint 3.7 Capability Reliability"
        )
        print(
            "-" * 60
        )
        print(
            report.summary
        )

        for line in report.lines:
            print(
                line
            )

        print(
            "Capability reliability gate: PASS"
        )

    finally:
        await app.shutdown()


if __name__ == "__main__":
    asyncio.run(
        main()
    )
