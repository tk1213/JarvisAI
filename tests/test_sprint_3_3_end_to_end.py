from __future__ import annotations

from typing import Any

import pytest

from jarvis.planner.backoff import BackoffPolicy
from jarvis.planner.executor import PlanExecutor
from jarvis.planner.models import (
    Plan,
    PlanStatus,
    PlanStep,
)
from jarvis.planner.recovery import RecoveryPlanner
from jarvis.planner.retry import RetryPolicy


class ScenarioRouter:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, Any]]] = []
        self.ping_attempts = 0

    async def execute_request(
        self,
        request,
    ) -> Any:
        self.calls.append(
            (
                request.capability,
                dict(request.arguments),
            )
        )

        if request.capability == "demo.resolve_device":
            return {
                "device": {
                    "id": "plug-001",
                    "name": "Smart Plug 1",
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


@pytest.mark.asyncio
async def test_context_and_retry_complete_successfully() -> None:
    router = ScenarioRouter()

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
        goal="Resolve device and ping system",
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

    assert result.success is True
    assert result.completed_steps == 2
    assert result.step_results[1].attempts == 2

    second_call = next(
    call
    for call in router.calls
    if call[0] == "system.ping"
)

    assert second_call[1] == {
        "device_id": "plug-001",
    }


@pytest.mark.asyncio
async def test_failed_plan_produces_recovery_review() -> None:
    router = ScenarioRouter()

    executor = PlanExecutor(
        router=router,  # type: ignore[arg-type]
        retry_policy=RetryPolicy(
            max_attempts=1
        ),
    )

    plan = Plan(
        goal="Change device then fail",
        steps=[
            PlanStep(
                index=1,
                capability="smart_home.turn_off",
                arguments={
                    "device_query": "Smart Plug 1",
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

    assert execution.success is False
    assert (
        assessment.requires_compensation_review
        is True
    )

    assert [
        candidate.capability
        for candidate
        in assessment.compensation.candidates
    ] == [
        "smart_home.turn_off",
    ]
