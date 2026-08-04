from __future__ import annotations

import asyncio
from typing import Any

from jarvis.planner.executor import PlanExecutor
from jarvis.planner.models import (
    Plan,
    PlanStatus,
    PlanStep,
)


class DemoRouter:
    async def execute_request(
        self,
        request,
    ) -> Any:
        print(
            "Executing: "
            f"{request.capability} "
            f"{request.arguments}"
        )

        if request.capability == "smart_home.turn_off":
            return {
                "success": True,
            }

        if request.capability == "smart_home.status":
            return {
                "power": False,
            }

        return None


async def main() -> None:
    plan = Plan(
        goal="Turn off bedroom light and check status",
        steps=[
            PlanStep(
                index=1,
                capability="smart_home.turn_off",
                arguments={
                    "device": "bedroom light",
                },
            ),
            PlanStep(
                index=2,
                capability="smart_home.status",
                arguments={
                    "device": "bedroom light",
                },
            ),
        ],
        status=PlanStatus.READY,
    )

    executor = PlanExecutor(
        DemoRouter(),  # type: ignore[arg-type]
    )

    result = await executor.execute(
        plan
    )

    print()
    print(
        f"Plan status: {result.plan.status.value}"
    )
    print(
        f"Success: {result.success}"
    )

    for step_result in result.step_results:
        print(
            f"{step_result.step_index}. "
            f"{step_result.capability} "
            f"success={step_result.success} "
            f"output={step_result.output!r} "
            f"error={step_result.error!r}"
        )


if __name__ == "__main__":
    asyncio.run(
        main()
    )
