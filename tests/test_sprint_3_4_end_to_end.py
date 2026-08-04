from __future__ import annotations

import asyncio
from typing import Any

import pytest

from jarvis.planner.backoff import BackoffPolicy
from jarvis.planner.bulkhead import (
    BulkheadPolicy,
    CapabilityBulkhead,
)
from jarvis.planner.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerPolicy,
)
from jarvis.planner.deadline import PlanDeadlinePolicy
from jarvis.planner.executor import PlanExecutor
from jarvis.planner.models import (
    Plan,
    PlanStatus,
    PlanStep,
)
from jarvis.planner.resilience_runtime import (
    ResilienceRuntime,
)
from jarvis.planner.retry import RetryPolicy
from jarvis.planner.timeout import ExecutionTimeoutPolicy


class ScenarioRouter:
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

        if request.capability == "system.ping":
            self.ping_attempts += 1

            if self.ping_attempts == 1:
                raise RuntimeError(
                    "temporary connection unavailable"
                )

            return {
                "status": "ok",
            }

        if request.capability == "system.version":
            raise RuntimeError(
                "invalid request"
            )

        if request.capability == "system.health":
            await asyncio.sleep(
                0.05
            )
            return {
                "healthy": True,
            }

        raise RuntimeError(
            f"unsupported capability: {request.capability}"
        )


def make_plan(
    capability: str,
) -> Plan:
    return Plan(
        goal=f"Test {capability}",
        steps=[
            PlanStep(
                index=1,
                capability=capability,
            )
        ],
        status=PlanStatus.READY,
    )


@pytest.mark.asyncio
async def test_retry_and_resilience_runtime_work_together() -> None:
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

    result = await executor.execute(
        make_plan(
            "system.ping"
        )
    )

    runtime = ResilienceRuntime()
    runtime.observe_execution(
        result
    )

    snapshot = runtime.snapshot()

    assert result.success is True
    assert result.step_results[0].attempts == 2
    assert snapshot.metrics.retries == 1
    assert snapshot.metrics.plans_completed == 1


@pytest.mark.asyncio
async def test_circuit_breaker_fails_fast_after_terminal_failure() -> None:
    router = ScenarioRouter()

    breaker = CircuitBreaker(
        CircuitBreakerPolicy(
            failure_threshold=1,
            recovery_timeout_seconds=60,
        )
    )

    executor = PlanExecutor(
        router=router,  # type: ignore[arg-type]
        circuit_breaker=breaker,
    )

    first = await executor.execute(
        make_plan(
            "system.version"
        )
    )

    second = await executor.execute(
        make_plan(
            "system.version"
        )
    )

    assert first.success is False
    assert second.success is False
    assert router.calls == [
        "system.version",
    ]
    assert (
        second.step_results[0].error
        == "capability circuit breaker is open"
    )


@pytest.mark.asyncio
async def test_bulkhead_rejects_concurrent_same_capability() -> None:
    router = ScenarioRouter()

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
            make_plan(
                "system.health"
            )
        )
    )

    await asyncio.sleep(
        0.005
    )

    second = await executor.execute(
        make_plan(
            "system.health"
        )
    )

    first = await first_task

    assert first.success is True
    assert second.success is False
    assert (
        second.step_results[0].error
        == "capability concurrency limit reached"
    )


@pytest.mark.asyncio
async def test_global_deadline_stops_slow_execution() -> None:
    router = ScenarioRouter()

    executor = PlanExecutor(
        router=router,  # type: ignore[arg-type]
        timeout_policy=ExecutionTimeoutPolicy(
            step_timeout_seconds=1.0
        ),
        deadline_policy=PlanDeadlinePolicy(
            plan_timeout_seconds=0.01
        ),
    )

    result = await executor.execute(
        make_plan(
            "system.health"
        )
    )

    assert result.success is False
    assert (
        "deadline exceeded"
        in result.step_results[0].error
    )
