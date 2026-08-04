from __future__ import annotations

import asyncio
from typing import Any

from jarvis.planner.backoff import BackoffPolicy
from jarvis.planner.bulkhead import (
    BulkheadPolicy,
    CapabilityBulkhead,
)
from jarvis.planner.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerPolicy,
)
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
        goal=f"Demo {capability}",
        steps=[
            PlanStep(
                index=1,
                capability=capability,
            )
        ],
        status=PlanStatus.READY,
    )


async def main() -> None:
    print(
        "Sprint 3.4 End-to-End Resilience Gate"
    )
    print(
        "=" * 60
    )

    router = DemoRouter()

    retry_executor = PlanExecutor(
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

    retry_result = await retry_executor.execute(
        make_plan(
            "system.ping"
        )
    )

    runtime = ResilienceRuntime()
    runtime.observe_execution(
        retry_result
    )

    retry_snapshot = runtime.snapshot()

    print(
        "[Gate 1] Retry + Metrics"
    )
    print(
        f"Plan status: {retry_result.plan.status.value}"
    )
    print(
        f"Attempts: {retry_result.step_results[0].attempts}"
    )
    print(
        f"Retries observed: {retry_snapshot.metrics.retries}"
    )

    breaker = CircuitBreaker(
        CircuitBreakerPolicy(
            failure_threshold=1,
            recovery_timeout_seconds=60,
        )
    )

    breaker_executor = PlanExecutor(
        router=router,  # type: ignore[arg-type]
        circuit_breaker=breaker,
    )

    first_failure = await breaker_executor.execute(
        make_plan(
            "system.version"
        )
    )

    second_failure = await breaker_executor.execute(
        make_plan(
            "system.version"
        )
    )

    print()
    print(
        "[Gate 2] Circuit Breaker"
    )
    print(
        f"First: {first_failure.plan.status.value}"
    )
    print(
        f"Second: {second_failure.plan.status.value}"
    )
    print(
        "Second error: "
        f"{second_failure.step_results[0].error}"
    )

    bulkhead = CapabilityBulkhead(
        BulkheadPolicy(
            max_concurrent_per_capability=1,
            acquire_timeout_seconds=0.01,
        )
    )

    bulkhead_executor = PlanExecutor(
        router=router,  # type: ignore[arg-type]
        bulkhead=bulkhead,
    )

    first_task = asyncio.create_task(
        bulkhead_executor.execute(
            make_plan(
                "system.health"
            )
        )
    )

    await asyncio.sleep(
        0.005
    )

    rejected = await bulkhead_executor.execute(
        make_plan(
            "system.health"
        )
    )

    first_ok = await first_task

    print()
    print(
        "[Gate 3] Bulkhead"
    )
    print(
        f"Primary: {first_ok.plan.status.value}"
    )
    print(
        f"Concurrent: {rejected.plan.status.value}"
    )
    print(
        "Concurrent error: "
        f"{rejected.step_results[0].error}"
    )

    if not retry_result.success:
        raise RuntimeError(
            "Retry gate failed."
        )

    if retry_snapshot.metrics.retries != 1:
        raise RuntimeError(
            "Retry metric gate failed."
        )

    if (
        second_failure.step_results[0].error
        != "capability circuit breaker is open"
    ):
        raise RuntimeError(
            "Circuit-breaker gate failed."
        )

    if (
        rejected.step_results[0].error
        != "capability concurrency limit reached"
    ):
        raise RuntimeError(
            "Bulkhead gate failed."
        )

    print()
    print(
        "Sprint 3.4 end-to-end gate: PASS"
    )


if __name__ == "__main__":
    asyncio.run(
        main()
    )
