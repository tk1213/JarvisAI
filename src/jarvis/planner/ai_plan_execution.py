from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from jarvis.planner.ai_plan_pipeline import (
    AIPlanPipeline,
    AIPlanPipelineResult,
)
from jarvis.planner.executor import PlanExecutionResult
from jarvis.planner.models import Plan


class PlanExecutionProtocol(Protocol):
    async def execute(
        self,
        plan: Plan,
    ) -> PlanExecutionResult:
        ...


@dataclass(slots=True, frozen=True)
class AIPlanExecutionResult:
    pipeline: AIPlanPipelineResult
    execution: PlanExecutionResult

    @property
    def success(self) -> bool:
        return self.execution.success

    @property
    def completed_steps(self) -> int:
        return self.execution.completed_steps


class AIPlanExecutionService:
    def __init__(
        self,
        *,
        pipeline: AIPlanPipeline,
        executor: PlanExecutionProtocol,
    ) -> None:
        self._pipeline = pipeline
        self._executor = executor

    async def execute(
        self,
        payload: str | dict[str, Any],
    ) -> AIPlanExecutionResult:
        pipeline_result = self._pipeline.build(
            payload
        )

        execution_result = await self._executor.execute(
            pipeline_result.adaptation.plan
        )

        return AIPlanExecutionResult(
            pipeline=pipeline_result,
            execution=execution_result,
        )
