from __future__ import annotations

from dataclasses import dataclass

from jarvis.planner.execution_health import (
    ExecutionHealthLevel,
)
from jarvis.planner.execution_persistence import (
    ExecutionPersistenceService,
)
from jarvis.planner.execution_record import (
    PlanExecutionRecord,
)


@dataclass(slots=True, frozen=True)
class ExecutionHealthWindow:
    size: int
    completed: int
    failed: int
    retries: int
    timeouts: int

    @property
    def success_rate(self) -> float:
        if self.size == 0:
            return 0.0

        return self.completed / self.size


@dataclass(slots=True, frozen=True)
class ExecutionHealthTrend:
    current: ExecutionHealthWindow
    previous: ExecutionHealthWindow
    direction: str
    level: ExecutionHealthLevel
    reason: str


class ExecutionHealthTrendService:
    def __init__(
        self,
        persistence: ExecutionPersistenceService,
    ) -> None:
        self._persistence = persistence

    async def summarize(
        self,
        *,
        window_size: int = 20,
    ) -> ExecutionHealthTrend:
        if window_size < 1:
            raise ValueError(
                "window_size must be at least 1."
            )

        records = await self._persistence.list_recent(
            limit=window_size * 2
        )

        current_records = records[
            :window_size
        ]
        previous_records = records[
            window_size:
            window_size * 2
        ]

        current = self._window(
            current_records
        )
        previous = self._window(
            previous_records
        )

        direction = self._direction(
            current=current,
            previous=previous,
        )

        level, reason = self._level(
            current=current,
            direction=direction,
        )

        return ExecutionHealthTrend(
            current=current,
            previous=previous,
            direction=direction,
            level=level,
            reason=reason,
        )

    @staticmethod
    def _window(
        records: list[PlanExecutionRecord],
    ) -> ExecutionHealthWindow:
        completed = sum(
            record.success
            for record in records
        )

        retries = 0
        timeouts = 0

        for record in records:
            for step in record.steps:
                if step.attempts > 1:
                    retries += 1

                if (
                    step.error is not None
                    and "timed out" in step.error.lower()
                ):
                    timeouts += 1

        return ExecutionHealthWindow(
            size=len(
                records
            ),
            completed=completed,
            failed=len(
                records
            ) - completed,
            retries=retries,
            timeouts=timeouts,
        )

    @staticmethod
    def _direction(
        *,
        current: ExecutionHealthWindow,
        previous: ExecutionHealthWindow,
    ) -> str:
        if previous.size == 0:
            return "unknown"

        delta = (
            current.success_rate
            - previous.success_rate
        )

        if delta >= 0.1:
            return "improving"

        if delta <= -0.1:
            return "worsening"

        return "stable"

    @staticmethod
    def _level(
        *,
        current: ExecutionHealthWindow,
        direction: str,
    ) -> tuple[
        ExecutionHealthLevel,
        str,
    ]:
        if current.size == 0:
            return (
                ExecutionHealthLevel.UNKNOWN,
                "No current execution history is available.",
            )

        if (
            current.success_rate < 0.5
            or current.timeouts >= 3
        ):
            return (
                ExecutionHealthLevel.UNHEALTHY,
                "Current execution window is below reliability thresholds.",
            )

        if (
            current.success_rate < 0.8
            or current.timeouts > 0
            or current.retries >= 3
            or direction == "worsening"
        ):
            return (
                ExecutionHealthLevel.DEGRADED,
                "Current execution window shows degraded reliability.",
            )

        return (
            ExecutionHealthLevel.HEALTHY,
            "Current execution window is within healthy limits.",
        )
