from __future__ import annotations

import asyncio
from typing import Any

from jarvis.planner.execution_record import PlanExecutionRecordBuilder
from jarvis.planner.execution_record_json import (
    PlanExecutionRecordJSONEncoder,
)
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
        return {
            "capability": request.capability,
            "status": "ok",
        }


async def main() -> None:
    executor = PlanExecutor(
        router=DemoRouter(),  # type: ignore[arg-type]
    )

    plan = Plan(
        goal="Create persistent execution record",
        steps=[
            PlanStep(
                index=1,
                capability="system.ping",
            )
        ],
        status=PlanStatus.READY,
    )

    execution = await executor.execute(
        plan
    )

    record = PlanExecutionRecordBuilder().build(
        execution
    )

    payload = PlanExecutionRecordJSONEncoder().dumps(
        record,
        indent=2,
    )

    print(
        "Sprint 3.5 Execution Record"
    )
    print(
        "-" * 60
    )
    print(
        f"Plan status: {record.plan_status}"
    )
    print(
        f"Completed steps: {record.completed_steps}"
    )
    print(
        f"Journal events: {len(record.events)}"
    )
    print(
        payload
    )

    if not record.success:
        raise RuntimeError(
            "Execution record gate failed."
        )

    print(
        "Execution record gate: PASS"
    )


if __name__ == "__main__":
    asyncio.run(
        main()
    )
