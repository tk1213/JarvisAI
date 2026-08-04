from __future__ import annotations

from jarvis.planner.execution_persistence import (
    ExecutionPersistenceService,
)
from jarvis.planner.executor import (
    PlanExecutionResult,
    PlanExecutor,
)
from jarvis.planner.models import Plan
from jarvis.services.capability_router import CapabilityRouter


class PersistingPlanExecutor(PlanExecutor):
    def __init__(
        self,
        router: CapabilityRouter,
        *,
        persistence: ExecutionPersistenceService,
    ) -> None:
        super().__init__(
            router
        )
        self._persistence = persistence

    async def execute(
        self,
        plan: Plan,
    ) -> PlanExecutionResult:
        result = await super().execute(
            plan
        )

        await self._persistence.persist_execution(
            result
        )

        return result
