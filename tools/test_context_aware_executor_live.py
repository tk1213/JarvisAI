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
            f"Executing: {request.capability} "
            f"{request.arguments}"
        )

        if request.capability == "demo.resolve_device":
            return {
                "device": {
                    "id": "plug-001",
                    "name": "Smart Plug 1",
                }
            }

        if request.capability == "demo.read_status":
            return {
                "device_id": request.arguments["device_id"],
                "power": False,
            }

        raise RuntimeError(
            f"Unsupported demo capability: {request.capability}"
        )


async def main() -> None:
    executor = PlanExecutor(
        router=DemoRouter(),  # type: ignore[arg-type]
    )

    plan = Plan(
        goal="Resolve a device then read its status",
        steps=[
            PlanStep(
                index=1,
                capability="demo.resolve_device",
                arguments={
                    "device_query": "Smart Plug 1",
                },
            ),
            PlanStep(
                index=2,
                capability="demo.read_status",
                arguments={
                    "device_id": {
                        "$step": "1.device.id",
                    }
                },
            ),
        ],
        status=PlanStatus.READY,
    )

    result = await executor.execute(plan)

    print()
    print("Sprint 3.3 Context-aware PlanExecutor")
    print("-" * 60)

    for step_result in result.step_results:
        print(
            f"Step {step_result.step_index}: "
            f"{step_result.status.value} "
            f"output={step_result.output!r}"
        )

    print(
        f"Plan status: {result.plan.status.value}"
    )

    if not result.success:
        raise RuntimeError(
            "Context-aware executor gate failed."
        )

    print(
        "Context-aware executor gate: PASS"
    )


if __name__ == "__main__":
    asyncio.run(main())
