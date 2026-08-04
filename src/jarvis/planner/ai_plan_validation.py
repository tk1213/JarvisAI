from __future__ import annotations

from dataclasses import dataclass

from jarvis.planner.ai_plan_contract import AIPlanDraft
from jarvis.services.capability_registry import CapabilityRegistry


@dataclass(slots=True, frozen=True)
class AIPlanValidationIssue:
    code: str
    message: str
    step_index: int | None = None
    capability: str | None = None


@dataclass(slots=True, frozen=True)
class AIPlanValidationResult:
    valid: bool
    issues: tuple[
        AIPlanValidationIssue,
        ...
    ]


class AIPlanValidator:
    def __init__(
        self,
        registry: CapabilityRegistry,
        *,
        max_steps: int = 20,
    ) -> None:
        if max_steps < 1:
            raise ValueError(
                "max_steps must be at least 1."
            )

        self._registry = registry
        self._max_steps = max_steps

    def validate(
        self,
        draft: AIPlanDraft,
    ) -> AIPlanValidationResult:
        issues: list[
            AIPlanValidationIssue
        ] = []

        if len(
            draft.steps
        ) > self._max_steps:
            issues.append(
                AIPlanValidationIssue(
                    code="too_many_steps",
                    message=(
                        "AI plan exceeds the maximum "
                        "allowed step count."
                    ),
                )
            )

        known = set(
            self._registry.list_capabilities()
        )

        for index, step in enumerate(
            draft.steps,
            start=1,
        ):
            if step.capability not in known:
                issues.append(
                    AIPlanValidationIssue(
                        code="unknown_capability",
                        message=(
                            "AI plan references an unknown "
                            f"capability: {step.capability}"
                        ),
                        step_index=index,
                        capability=step.capability,
                    )
                )

        return AIPlanValidationResult(
            valid=not issues,
            issues=tuple(
                issues
            ),
        )
