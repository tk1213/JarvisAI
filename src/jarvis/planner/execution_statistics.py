from __future__ import annotations

from dataclasses import dataclass

from jarvis.planner.execution_persistence import (
    ExecutionPersistenceService,
)
from jarvis.planner.execution_record import (
    PlanExecutionRecord,
)


@dataclass(slots=True, frozen=True)
class ExecutionStatistics:
    total: int
    completed: int
    failed: int
    retried_steps: int
    timed_out_steps: int
    capability_counts: dict[str, int]
    capability_failure_counts: dict[str, int]

    @property
    def success_rate(self) -> float:
        if self.total == 0:
            return 0.0

        return self.completed / self.total


class ExecutionStatisticsService:
    def __init__(
        self,
        persistence: ExecutionPersistenceService,
    ) -> None:
        self._persistence = persistence

    async def summarize(
        self,
        *,
        limit: int = 100,
    ) -> ExecutionStatistics:
        if limit < 1:
            raise ValueError(
                "limit must be at least 1."
            )

        records = await self._persistence.list_recent(
            limit=limit
        )

        return self._build(
            records
        )

    @staticmethod
    def _build(
        records: list[PlanExecutionRecord],
    ) -> ExecutionStatistics:
        completed = sum(
            record.success
            for record in records
        )

        failed = len(
            records
        ) - completed

        retried_steps = 0
        timed_out_steps = 0
        capability_counts: dict[str, int] = {}
        capability_failure_counts: dict[str, int] = {}

        for record in records:
            for step in record.steps:
                capability_counts[
                    step.capability
                ] = (
                    capability_counts.get(
                        step.capability,
                        0,
                    )
                    + 1
                )

                if step.attempts > 1:
                    retried_steps += 1

                if (
                    step.error is not None
                    and "timed out" in step.error.lower()
                ):
                    timed_out_steps += 1

                if step.status == "failed":
                    capability_failure_counts[
                        step.capability
                    ] = (
                        capability_failure_counts.get(
                            step.capability,
                            0,
                        )
                        + 1
                    )

        return ExecutionStatistics(
            total=len(
                records
            ),
            completed=completed,
            failed=failed,
            retried_steps=retried_steps,
            timed_out_steps=timed_out_steps,
            capability_counts=capability_counts,
            capability_failure_counts=(
                capability_failure_counts
            ),
        )
