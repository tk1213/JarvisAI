from __future__ import annotations

from jarvis.core.logger import log
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
        self._last_persistence_error: str | None = None

    @property
    def last_persistence_error(
        self,
    ) -> str | None:
        return self._last_persistence_error

    async def execute(
        self,
        plan: Plan,
    ) -> PlanExecutionResult:
        result = await super().execute(
            plan
        )

        self._last_persistence_error = None

        try:
            await self._persistence.persist_execution(
                result
            )

        except Exception as exc:  # noqa: BLE001
            self._last_persistence_error = str(
                exc
            )

            log.exception(
                "Plan execution persistence failed after execution "
                "completed; returning the completed execution result."
            )

        return result