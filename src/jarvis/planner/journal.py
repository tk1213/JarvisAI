from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any


class ExecutionEventType(StrEnum):
    PLAN_STARTED = "plan_started"
    STEP_STARTED = "step_started"
    STEP_RETRYING = "step_retrying"
    STEP_COMPLETED = "step_completed"
    STEP_FAILED = "step_failed"
    PLAN_COMPLETED = "plan_completed"
    PLAN_FAILED = "plan_failed"


@dataclass(slots=True, frozen=True)
class ExecutionEvent:
    sequence: int
    event_type: ExecutionEventType
    timestamp: datetime
    step_index: int | None = None
    capability: str | None = None
    attempt: int | None = None
    details: dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        if self.sequence < 1:
            raise ValueError(
                "Execution event sequence must be at least 1."
            )

        if (
            self.step_index is not None
            and self.step_index < 1
        ):
            raise ValueError(
                "Execution event step_index must be at least 1."
            )

        if (
            self.attempt is not None
            and self.attempt < 1
        ):
            raise ValueError(
                "Execution event attempt must be at least 1."
            )


class ExecutionJournal:
    def __init__(self) -> None:
        self._events: list[ExecutionEvent] = []

    @property
    def events(self) -> tuple[ExecutionEvent, ...]:
        return tuple(
            self._events
        )

    def record(
        self,
        event_type: ExecutionEventType,
        *,
        step_index: int | None = None,
        capability: str | None = None,
        attempt: int | None = None,
        details: dict[str, Any] | None = None,
    ) -> ExecutionEvent:
        event = ExecutionEvent(
            sequence=len(self._events) + 1,
            event_type=event_type,
            timestamp=datetime.now(UTC),
            step_index=step_index,
            capability=capability,
            attempt=attempt,
            details=(
                dict(details)
                if details is not None
                else {}
            ),
        )

        self._events.append(
            event
        )

        from jarvis.planner.resilience_runtime import (
            resilience_runtime,
        )

        resilience_runtime.observe_event(
            event
        )

        return event
