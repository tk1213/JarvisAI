from __future__ import annotations

import asyncio
from typing import Any

from jarvis.planner.deadline import PlanDeadlinePolicy
from jarvis.planner.executor import PlanExecutor
from jarvis.planner.models import (
    Plan,
    PlanStatus,
    PlanStep,
)
from jarvis.planner.timeout import ExecutionTimeoutPolicy


class DemoSlowRouter:
    def __init__(self) -> None:
        self.calls = 0

    async def execute_request(
        self,
        request,
    ) -> Any:
        self.calls += 1

        print(
            f"Call {self.calls}: "
            f"{request.capability}"
        )

        await asyncio.sleep(
            0.05
        )

        return {
            "status": "late",
        }


async def main() -> None:
    router = DemoSlowRouter()

    executor = PlanExecutor(
        router=router,  # type: ignore[arg-type]
        timeout_policy=ExecutionTimeoutPolicy(
            step_timeout_seconds=1.0
        ),
        deadline_policy=PlanDeadlinePolicy(
            plan_timeout_seconds=0.01
        ),
    )

    plan = Plan(
        goal="Demonstrate global plan deadline",
        steps=[
            PlanStep(
                index=1,
                capability="system.ping",
            ),
            PlanStep(
                index=2,
                capability="system.version",
            ),
        ],
        status=PlanStatus.READY,
    )

    result = await executor.execute(
        plan
    )

    print()
    print(
        "Sprint 3.4 Plan Deadline"
    )
    print(
        "-" * 60
    )
    print(
        f"Plan status: {result.plan.status.value}"
    )
    print(
        f"Router calls: {router.calls}"
    )
    print(
        f"Error: {result.step_results[0].error}"
    )

    if result.success:
        raise RuntimeError(
            "Plan deadline gate unexpectedly succeeded."
        )

    if router.calls != 1:
        raise RuntimeError(
            "Plan deadline did not stop later execution."
        )

    print(
        "Plan deadline gate: PASS"
    )


if __name__ == "__main__":
    asyncio.run(
        main()
    )
