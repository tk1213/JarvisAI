from __future__ import annotations

import asyncio
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

@pytest.mark.asyncio
async def test_persistence_failure_does_not_fail_completed_execution() -> None:
    class FailingPersistence:
        async def persist_execution(
            self,
            execution: PlanExecutionResult,
        ) -> int:
            assert execution.success is True

            raise RuntimeError(
                "persistence failed"
            )

    executor = PersistingPlanExecutor(
        DemoRouter(),  # type: ignore[arg-type]
        persistence=FailingPersistence(),  # type: ignore[arg-type]
    )

    plan = Plan(
        goal="Persistence failure",
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
    assert plan.status is PlanStatus.COMPLETED
    assert executor.last_persistence_error == "persistence failed"
    

@pytest.mark.asyncio
async def test_persistence_cancellation_propagates_after_execution_completes() -> None:
    class CancellingPersistence:
        async def persist_execution(
            self,
            execution: PlanExecutionResult,
        ) -> int:
            assert execution.success is True
            raise asyncio.CancelledError

    executor = PersistingPlanExecutor(
        DemoRouter(),  # type: ignore[arg-type]
        persistence=CancellingPersistence(),  # type: ignore[arg-type]
    )

    plan = Plan(
        goal="Persistence cancellation",
        steps=[
            PlanStep(
                index=1,
                capability="system.ping",
            )
        ],
        status=PlanStatus.READY,
    )

    with pytest.raises(
        asyncio.CancelledError,
    ):
        await executor.execute(
            plan
        )

    assert plan.status is PlanStatus.COMPLETED
    assert executor.last_persistence_error is None

@pytest.mark.asyncio
async def test_persistence_failure_does_not_hide_failed_execution_result() -> None:
    class FailingRouter:
        async def execute_request(
            self,
            request,
        ) -> Any:
            del request

            raise RuntimeError(
                "execution failed"
            )

    class FailingPersistence:
        async def persist_execution(
            self,
            execution: PlanExecutionResult,
        ) -> int:
            assert execution.success is False

            raise RuntimeError(
                "persistence failed"
            )

    executor = PersistingPlanExecutor(
        FailingRouter(),  # type: ignore[arg-type]
        persistence=FailingPersistence(),  # type: ignore[arg-type]
    )

    plan = Plan(
        goal="Failed execution with persistence failure",
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
    assert plan.status is PlanStatus.FAILED
    assert executor.last_persistence_error == "persistence failed"