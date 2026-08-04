from __future__ import annotations

import asyncio
from typing import Any

import pytest

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


class SlowRouter:
    def __init__(self) -> None:
        self.calls = 0

    async def execute_request(
        self,
        request,
    ) -> Any:
        del request
        self.calls += 1
        await asyncio.sleep(
            0.05
        )
        return {
            "ok": True,
        }


def make_plan() -> Plan:
    return Plan(
        goal="Concurrent ping",
        steps=[
            PlanStep(
                index=1,
                capability="system.ping",
            )
        ],
        status=PlanStatus.READY,
    )


@pytest.mark.asyncio
async def test_second_execution_fails_fast_on_bulkhead() -> None:
    router = SlowRouter()
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

    assert first_result.success is True
    assert second_result.success is False
    assert router.calls == 1
    assert (
        second_result.step_results[0].error
        == "capability concurrency limit reached"
    )
