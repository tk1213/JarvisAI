from __future__ import annotations

from dataclasses import dataclass

from jarvis.planner.execution_persistence import (
    ExecutionPersistenceService,
)
from jarvis.planner.execution_record import (
    PlanExecutionRecord,
)


@dataclass(slots=True, frozen=True)
class CapabilityReliability:
    capability: str
    executions: int
    failures: int
    retries: int
    timeouts: int

    @property
    def success_rate(self) -> float:
        if self.executions == 0:
            return 0.0

        return (
            self.executions - self.failures
        ) / self.executions


@dataclass(slots=True, frozen=True)
class CapabilityReliabilitySummary:
    total_capabilities: int
    capabilities: tuple[
        CapabilityReliability,
        ...
    ]


class CapabilityReliabilityService:
    def __init__(
        self,
        persistence: ExecutionPersistenceService,
    ) -> None:
        self._persistence = persistence

    async def summarize(
        self,
        *,
        limit: int = 100,
    ) -> CapabilityReliabilitySummary:
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
    ) -> CapabilityReliabilitySummary:
        counters: dict[
            str,
            dict[str, int],
        ] = {}

        for record in records:
            for step in record.steps:
                values = counters.setdefault(
                    step.capability,
                    {
                        "executions": 0,
                        "failures": 0,
                        "retries": 0,
                        "timeouts": 0,
                    },
                )

                values["executions"] += 1

                if step.status == "failed":
                    values["failures"] += 1

                if step.attempts > 1:
                    values["retries"] += 1

                if (
                    step.error is not None
                    and "timed out" in step.error.lower()
                ):
                    values["timeouts"] += 1

        capabilities = tuple(
            CapabilityReliability(
                capability=capability,
                executions=values["executions"],
                failures=values["failures"],
                retries=values["retries"],
                timeouts=values["timeouts"],
            )
            for capability, values in sorted(
                counters.items()
            )
        )

        return CapabilityReliabilitySummary(
            total_capabilities=len(
                capabilities
            ),
            capabilities=capabilities,
        )
