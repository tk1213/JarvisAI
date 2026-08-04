from __future__ import annotations

from typing import Any

import pytest

from jarvis.planner.backoff import BackoffPolicy
from jarvis.planner.executor import PlanExecutor
from jarvis.planner.journal import ExecutionEventType
from jarvis.planner.models import (
    Plan,
    PlanStatus,
    PlanStep,
)
from jarvis.planner.retry import RetryPolicy


class FlakyRouter:
    def __init__(
        self,
        *,
        failures_before_success: int,
    ) -> None:
        self.failures_before_success = (
            failures_before_success
        )
        self.calls = 0

    async def execute_request(
        self,
        request,
    ) -> Any:
        del request

        self.calls += 1

        if self.calls <= self.failures_before_success:
            raise RuntimeError(
                "temporary connection unavailable"
            )

        return {
            "status": "ok",
        }


@pytest.mark.asyncio
async def test_successful_execution_records_journal() -> None:
    router = FlakyRouter(
        failures_before_success=0
    )

    executor = PlanExecutor(
        router=router,  # type: ignore[arg-type]
    )

    plan = Plan(
        goal="Ping system",
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

    event_types = [
        event.event_type
        for event in result.journal_events
    ]

    assert event_types == [
        ExecutionEventType.PLAN_STARTED,
        ExecutionEventType.STEP_STARTED,
        ExecutionEventType.STEP_COMPLETED,
        ExecutionEventType.PLAN_COMPLETED,
    ]


@pytest.mark.asyncio
async def test_retry_is_recorded_in_journal() -> None:
    router = FlakyRouter(
        failures_before_success=1
    )

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
        goal="Retry ping",
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

    retry_events = [
        event
        for event in result.journal_events
        if (
            event.event_type
            is ExecutionEventType.STEP_RETRYING
        )
    ]

    assert len(retry_events) == 1
    assert retry_events[0].attempt == 1
    assert (
        retry_events[0].details[
            "failure_kind"
        ]
        == "transient"
    )


@pytest.mark.asyncio
async def test_failed_execution_records_plan_failure() -> None:
    router = FlakyRouter(
        failures_before_success=10
    )

    executor = PlanExecutor(
        router=router,  # type: ignore[arg-type]
        retry_policy=RetryPolicy(
            max_attempts=1
        ),
    )

    plan = Plan(
        goal="Fail ping",
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

    assert (
        result.journal_events[-1].event_type
        is ExecutionEventType.PLAN_FAILED
    )
