from __future__ import annotations

from typing import Any

import pytest

from jarvis.planner.executor import PlanExecutionResult
from jarvis.planner.models import (
    Plan,
    PlanStatus,
    PlanStep,
)
from jarvis.planner.persisting_executor import (
    PersistingPlanExecutor,
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


class FakePersistence:
    def __init__(self) -> None:
        self.executions: list[
            PlanExecutionResult
        ] = []

    async def persist_execution(
        self,
        execution: PlanExecutionResult,
    ) -> int:
        self.executions.append(
            execution
        )
        return len(
            self.executions
        )


@pytest.mark.asyncio
async def test_executor_persists_completed_execution() -> None:
    persistence = FakePersistence()

    executor = PersistingPlanExecutor(
        DemoRouter(),  # type: ignore[arg-type]
        persistence=persistence,  # type: ignore[arg-type]
    )

    plan = Plan(
        goal="Persist automatically",
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

    assert result.success is True
    assert len(
        persistence.executions
    ) == 1
    assert (
        persistence.executions[0]
        is result
    )


@pytest.mark.asyncio
async def test_executor_persists_failed_execution() -> None:
    class FailingRouter:
        async def execute_request(
            self,
            request,
        ) -> Any:
            del request
            raise RuntimeError(
                "invalid request"
            )

    persistence = FakePersistence()

    executor = PersistingPlanExecutor(
        FailingRouter(),  # type: ignore[arg-type]
        persistence=persistence,  # type: ignore[arg-type]
    )

    plan = Plan(
        goal="Persist failure",
        steps=[
            PlanStep(
                index=1,
                capability="system.version",
            )
        ],
        status=PlanStatus.READY,
    )

    result = await executor.execute(
        plan
    )

    assert result.success is False
    assert len(
        persistence.executions
    ) == 1
    assert (
        persistence.executions[0]
        is result
    )
