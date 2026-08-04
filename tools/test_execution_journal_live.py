from __future__ import annotations

import asyncio
from typing import Any

from jarvis.planner.backoff import BackoffPolicy
from jarvis.planner.executor import PlanExecutor
from jarvis.planner.models import (
    Plan,
    PlanStatus,
    PlanStep,
)
from jarvis.planner.retry import RetryPolicy


class DemoRouter:
    def __init__(self) -> None:
        self.calls = 0

    async def execute_request(
        self,
        request,
    ) -> Any:
        self.calls += 1

        if self.calls == 1:
            raise RuntimeError(
                "temporary connection unavailable"
            )

        return {
            "status": "ok",
        }


async def main() -> None:
    executor = PlanExecutor(
        router=DemoRouter(),  # type: ignore[arg-type]
        retry_policy=RetryPolicy(
            max_attempts=2
        ),
        backoff_policy=BackoffPolicy(
            base_delay_seconds=0,
            multiplier=1,
            max_delay_seconds=0,
        ),
    )

    plan = Plan(
        goal="Demonstrate execution journal",
        steps=[
            PlanStep(
                index=1,
                capability="system.ping",
            )
        ],
        status=PlanStatus.READY,
    )

    result = await executor.execute(
        plan
    )

    print(
        "Sprint 3.3 Execution Journal"
    )
    print(
        "-" * 60
    )

    for event in result.journal_events:
        print(
            f"{event.sequence}. "
            f"{event.event_type.value} "
            f"step={event.step_index} "
            f"attempt={event.attempt} "
            f"details={event.details}"
        )

    if not result.success:
        raise RuntimeError(
            "Execution journal gate failed."
        )

    print(
        "Execution journal gate: PASS"
    )


if __name__ == "__main__":
    asyncio.run(
        main()
    )
