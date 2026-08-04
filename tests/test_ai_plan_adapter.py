import pytest

from jarvis.planner.ai_plan_adapter import (
    AIPlanAdaptationError,
    AIPlanAdapter,
)
from jarvis.planner.ai_plan_contract import (
    AIPlanDraft,
    AIPlanStepDraft,
)
from jarvis.planner.ai_plan_validation import AIPlanValidator
from jarvis.planner.service import PlannerService
from jarvis.services.capability import CapabilityDefinition
from jarvis.services.capability_registry import CapabilityRegistry


def make_registry() -> CapabilityRegistry:
    return CapabilityRegistry(
        [
            CapabilityDefinition(
                name="system.ping",
            ),
            CapabilityDefinition(
                name="system.health",
            ),
        ]
    )


def make_adapter() -> AIPlanAdapter:
    registry = make_registry()

    return AIPlanAdapter(
        validator=AIPlanValidator(
            registry
        ),
        planner=PlannerService(
            registry
        ),
    )


def test_adapter_converts_draft_to_plan() -> None:
    result = make_adapter().adapt(
        AIPlanDraft(
            goal="Check Jarvis",
            steps=(
                AIPlanStepDraft(
                    capability="system.ping",
                    arguments={},
                    description="Ping Jarvis",
                ),
                AIPlanStepDraft(
                    capability="system.health",
                    arguments={},
                    description="Read health",
                ),
            ),
        )
    )

    assert result.validation.valid is True
    assert result.plan.goal == "Check Jarvis"
    assert len(
        result.plan.steps
    ) == 2
    assert result.plan.steps[0].capability == (
        "system.ping"
    )


def test_adapter_rejects_unknown_capability() -> None:
    with pytest.raises(
        AIPlanAdaptationError,
        match="unknown capability",
    ):
        make_adapter().adapt(
            AIPlanDraft(
                goal="Unknown",
                steps=(
                    AIPlanStepDraft(
                        capability="system.unknown",
                    ),
                ),
            )
        )
