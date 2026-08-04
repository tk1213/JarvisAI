from __future__ import annotations

import asyncio
from typing import Any

from jarvis.planner.executor import PlanExecutor
from jarvis.planner.models import (
    Plan,
    PlanStatus,
    PlanStep,
)
from jarvis.planner.recovery import RecoveryPlanner
from jarvis.planner.retry import RetryPolicy


class DemoRouter:
    def __init__(self) -> None:
        self.calls: list[str] = []

    async def execute_request(
        self,
        request,
    ) -> Any:
        self.calls.append(
            request.capability
        )

        if (
            request.capability
            == "smart_home.turn_off"
        ):
            return {
                "status": "off",
            }

        raise RuntimeError(
            "invalid request"
        )


async def main() -> None:
    router = DemoRouter()

    executor = PlanExecutor(
        router=router,  # type: ignore[arg-type]
        retry_policy=RetryPolicy(
            max_attempts=1
        ),
    )

    plan = Plan(
        goal="Demonstrate recovery assessment",
        steps=[
            PlanStep(
                index=1,
                capability="smart_home.turn_off",
                arguments={
                    "device_query": "Demo Plug",
                },
            ),
            PlanStep(
                index=2,
                capability="system.ping",
            ),
        ],
        status=PlanStatus.READY,
    )

    execution = await executor.execute(
        plan
    )

    assessment = RecoveryPlanner().assess(
        execution
    )

    print(
        "Sprint 3.3 Recovery Planning"
    )
    print(
        "-" * 60
    )
    print(
        f"Plan status: {execution.plan.status.value}"
    )
    print(
        "Requires compensation review: "
        f"{assessment.requires_compensation_review}"
    )

    for candidate in (
        assessment.compensation.candidates
    ):
        print(
            "Candidate: "
            f"step={candidate.step_index} "
            f"capability={candidate.capability} "
            f"arguments={candidate.arguments}"
        )

    print(
        f"Router calls: {router.calls}"
    )

    if not (
        assessment.requires_compensation_review
    ):
        raise RuntimeError(
            "Recovery planning gate failed."
        )

    if router.calls != [
        "smart_home.turn_off",
        "system.ping",
    ]:
        raise RuntimeError(
            "Recovery planner executed an "
            "unexpected capability."
        )

    print(
        "Recovery planning gate: PASS"
    )


if __name__ == "__main__":
    asyncio.run(
        main()
    )
