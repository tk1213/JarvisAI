from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class PlanStatus(StrEnum):
    DRAFT = "draft"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PlanStepStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass(slots=True)
class PlanStep:
    index: int
    capability: str
    arguments: dict[str, Any] = field(
        default_factory=dict
    )
    description: str = ""
    status: PlanStepStatus = PlanStepStatus.PENDING

    def __post_init__(self) -> None:
        if self.index < 1:
            raise ValueError(
                "Plan step index must be at least 1."
            )

        self.capability = self.capability.strip()

        if not self.capability:
            raise ValueError(
                "Plan step capability cannot be empty."
            )

        self.description = self.description.strip()


@dataclass(slots=True)
class Plan:
    goal: str
    steps: list[PlanStep]
    status: PlanStatus = PlanStatus.DRAFT

    def __post_init__(self) -> None:
        self.goal = self.goal.strip()

        if not self.goal:
            raise ValueError(
                "Plan goal cannot be empty."
            )

        if not self.steps:
            raise ValueError(
                "Plan must contain at least one step."
            )

        expected_indexes = list(
            range(
                1,
                len(self.steps) + 1,
            )
        )
        actual_indexes = [
            step.index
            for step in self.steps
        ]

        if actual_indexes != expected_indexes:
            raise ValueError(
                "Plan step indexes must be sequential "
                "starting at 1."
            )
