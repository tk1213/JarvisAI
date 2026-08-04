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
from jarvis.planner.recovery import RecoveryPlanner
from jarvis.planner.recovery_report import RecoveryReportBuilder
from jarvis.planner.retry import RetryPolicy


class DemoRouter:
    def __init__(self) -> None:
        self.calls: list[str] = []
        self.ping_attempts = 0

    async def execute_request(
        self,
        request,
    ) -> Any:
        self.calls.append(
            request.capability
        )

        if request.capability == "demo.resolve_device":
            return {
                "device": {
                    "id": "plug-001",
                }
            }

        if request.capability == "system.ping":
            self.ping_attempts += 1

            if self.ping_attempts == 1:
                raise RuntimeError(
                    "temporary connection unavailable"
                )

            return {
                "status": "ok",
            }

        if request.capability == "smart_home.turn_off":
            return {
                "status": "off",
            }

        if request.capability == "system.version":
            raise RuntimeError(
                "invalid request"
            )

        raise RuntimeError(
            f"unsupported capability: {request.capability}"
        )


async def run_success_scenario() -> None:
    router = DemoRouter()

    executor = PlanExecutor(
        router=router,  # type: ignore[arg-type]
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
        goal="Resolve device and ping",
        steps=[
            PlanStep(
                index=1,
                capability="demo.resolve_device",
            ),
            PlanStep(
                index=2,
                capability="system.ping",
                arguments={
                    "device_id": {
                        "$step": "1.device.id",
                    }
                },
            ),
        ],
        status=PlanStatus.READY,
    )

    result = await executor.execute(
        plan
    )

    print(
        "[Scenario 1] Context + Retry"
    )
    print(
        f"Plan status: {result.plan.status.value}"
    )
    print(
        f"Step 2 attempts: {result.step_results[1].attempts}"
    )

    if not result.success:
        raise RuntimeError(
            "Success scenario failed."
        )


async def run_recovery_scenario() -> None:
    router = DemoRouter()

    executor = PlanExecutor(
        router=router,  # type: ignore[arg-type]
        retry_policy=RetryPolicy(
            max_attempts=1
        ),
    )

    plan = Plan(
        goal="Change then fail",
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
                capability="system.version",
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

    report = RecoveryReportBuilder().build(
        assessment
    )

    print()
    print(
        "[Scenario 2] Recovery Assessment"
    )
    print(
        f"Plan status: {execution.plan.status.value}"
    )
    print(
        "Requires compensation review: "
        f"{assessment.requires_compensation_review}"
    )
    print(
        f"Recovery summary: {report.summary}"
    )

    for detail in report.details:
        print(
            f"- {detail}"
        )

    if not assessment.requires_compensation_review:
        raise RuntimeError(
            "Recovery assessment failed."
        )


async def main() -> None:
    print(
        "Sprint 3.3 End-to-End Gate"
    )
    print(
        "=" * 60
    )

    await run_success_scenario()
    await run_recovery_scenario()

    print()
    print(
        "Sprint 3.3 end-to-end gate: PASS"
    )


if __name__ == "__main__":
    asyncio.run(
        main()
    )
