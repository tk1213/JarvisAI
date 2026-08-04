from __future__ import annotations

import asyncio
from typing import Any

from jarvis.planner.bulkhead import (
    BulkheadPolicy,
    CapabilityBulkhead,
)
from jarvis.planner.executor import PlanExecutor
from jarvis.planner.models import (
    Plan,
    PlanStatus,
    PlanStep,
)


class DemoSlowRouter:
    def __init__(self) -> None:
        self.calls = 0

    async def execute_request(
        self,
        request,
    ) -> Any:
        self.calls += 1

        print(
            f"Router call {self.calls}: "
            f"{request.capability}"
        )

        await asyncio.sleep(
            0.05
        )

        return {
            "status": "ok",
        }


def make_plan() -> Plan:
    return Plan(
        goal="Bulkhead demo",
        steps=[
            PlanStep(
                index=1,
                capability="system.ping",
            )
        ],
        status=PlanStatus.READY,
    )


async def main() -> None:
    router = DemoSlowRouter()

    bulkhead = CapabilityBulkhead(
        BulkheadPolicy(
            max_concurrent_per_capability=1,
            acquire_timeout_seconds=0.01,
        )
    )

    executor = PlanExecutor(
        router=router,  # type: ignore[arg-type]
        bulkhead=bulkhead,
    )

    first_task = asyncio.create_task(
        executor.execute(
            make_plan()
        )
    )

    await asyncio.sleep(
        0.005
    )

    second_result = await executor.execute(
        make_plan()
    )

    first_result = await first_task

    print()
    print(
        "Sprint 3.4 Capability Bulkhead"
    )
    print(
        "-" * 60
    )
    print(
        f"First plan: {first_result.plan.status.value}"
    )
    print(
        f"Second plan: {second_result.plan.status.value}"
    )
    print(
        f"Router calls: {router.calls}"
    )
    print(
        "Second error: "
        f"{second_result.step_results[0].error}"
    )

    if not first_result.success:
        raise RuntimeError(
            "Primary execution unexpectedly failed."
        )

    if second_result.success:
        raise RuntimeError(
            "Bulkhead did not reject concurrent execution."
        )

    if router.calls != 1:
        raise RuntimeError(
            "Rejected execution reached the router."
        )

    print(
        "Capability bulkhead gate: PASS"
    )


if __name__ == "__main__":
    asyncio.run(
        main()
    )
