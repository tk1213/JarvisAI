from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True, frozen=True)
class AIPlanStepDraft:
    capability: str
    arguments: dict[str, Any] = field(
        default_factory=dict,
    )
    description: str = ""

    def __post_init__(self) -> None:
        capability = self.capability.strip()
        description = self.description.strip()

        if not capability:
            raise ValueError(
                "AI plan step capability cannot be empty."
            )

        object.__setattr__(
            self,
            "capability",
            capability,
        )
        object.__setattr__(
            self,
            "description",
            description,
        )
        object.__setattr__(
            self,
            "arguments",
            dict(
                self.arguments
            ),
        )


@dataclass(slots=True, frozen=True)
class AIPlanDraft:
    goal: str
    steps: tuple[
        AIPlanStepDraft,
        ...
    ]
    reasoning_summary: str = ""

    def __post_init__(self) -> None:
        goal = self.goal.strip()
        reasoning_summary = self.reasoning_summary.strip()

        if not goal:
            raise ValueError(
                "AI plan goal cannot be empty."
            )

        if not self.steps:
            raise ValueError(
                "AI plan must contain at least one step."
            )

        object.__setattr__(
            self,
            "goal",
            goal,
        )
        object.__setattr__(
            self,
            "reasoning_summary",
            reasoning_summary,
        )
        object.__setattr__(
            self,
            "steps",
            tuple(
                self.steps
            ),
        )
