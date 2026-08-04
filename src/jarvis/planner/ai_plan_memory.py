from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from jarvis.planner.ai_plan_execution import (
    AIPlanExecutionResult,
)
from jarvis.planner.ai_plan_reflection import (
    AIPlanReflectionResult,
)


@dataclass(slots=True, frozen=True)
class AIPlanMemoryRecord:
    goal: str
    capabilities: tuple[str, ...]
    success: bool
    completed_steps: int
    failed_steps: int
    reflection_decision: str
    created_at: datetime
    metadata: dict[str, Any]


@dataclass(slots=True, frozen=True)
class AIPlanMemoryQuery:
    goal_contains: str | None = None
    capability: str | None = None
    success: bool | None = None
    limit: int = 20


class AIPlanMemoryStore:
    def __init__(
        self,
        *,
        max_records: int = 500,
    ) -> None:
        if max_records < 1:
            raise ValueError(
                "max_records must be at least 1."
            )

        self._max_records = max_records
        self._records: list[
            AIPlanMemoryRecord
        ] = []

    def remember(
        self,
        *,
        execution: AIPlanExecutionResult,
        reflection: AIPlanReflectionResult,
        metadata: dict[str, Any] | None = None,
        created_at: datetime | None = None,
    ) -> AIPlanMemoryRecord:
        timestamp = (
            created_at
            if created_at is not None
            else datetime.now(UTC)
        )

        if timestamp.tzinfo is None:
            raise ValueError(
                "created_at must be timezone-aware."
            )

        record = AIPlanMemoryRecord(
            goal=execution.execution.plan.goal,
            capabilities=tuple(
                step.capability
                for step in execution.execution.plan.steps
            ),
            success=execution.success,
            completed_steps=execution.completed_steps,
            failed_steps=reflection.failed_steps,
            reflection_decision=reflection.decision.value,
            created_at=timestamp,
            metadata=dict(
                metadata or {}
            ),
        )

        self._records.append(
            record
        )

        overflow = (
            len(
                self._records
            )
            - self._max_records
        )

        if overflow > 0:
            del self._records[
                :overflow
            ]

        return record

    def query(
        self,
        query: AIPlanMemoryQuery,
    ) -> tuple[
        AIPlanMemoryRecord,
        ...
    ]:
        if query.limit < 1:
            raise ValueError(
                "query limit must be at least 1."
            )

        goal_filter = (
            query.goal_contains.casefold()
            if query.goal_contains is not None
            else None
        )

        capability_filter = (
            query.capability.strip()
            if query.capability is not None
            else None
        )

        matches = []

        for record in reversed(
            self._records
        ):
            if (
                goal_filter is not None
                and goal_filter
                not in record.goal.casefold()
            ):
                continue

            if (
                capability_filter is not None
                and capability_filter
                not in record.capabilities
            ):
                continue

            if (
                query.success is not None
                and record.success
                is not query.success
            ):
                continue

            matches.append(
                record
            )

            if len(
                matches
            ) >= query.limit:
                break

        return tuple(
            matches
        )

    def list_recent(
        self,
        *,
        limit: int = 20,
    ) -> tuple[
        AIPlanMemoryRecord,
        ...
    ]:
        return self.query(
            AIPlanMemoryQuery(
                limit=limit
            )
        )

    def clear(
        self,
    ) -> None:
        self._records.clear()

    def __len__(
        self,
    ) -> int:
        return len(
            self._records
        )
