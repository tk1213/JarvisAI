from jarvis.planner.ai_plan_contract import (
    AIPlanDraft,
    AIPlanStepDraft,
)
from jarvis.planner.ai_plan_validation import AIPlanValidator
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


def test_validator_accepts_known_capabilities() -> None:
    result = AIPlanValidator(
        make_registry()
    ).validate(
        AIPlanDraft(
            goal="Check Jarvis",
            steps=(
                AIPlanStepDraft(
                    capability="system.ping",
                ),
                AIPlanStepDraft(
                    capability="system.health",
                ),
            ),
        )
    )

    assert result.valid is True
    assert result.issues == ()


def test_validator_rejects_unknown_capability() -> None:
    result = AIPlanValidator(
        make_registry()
    ).validate(
        AIPlanDraft(
            goal="Unknown",
            steps=(
                AIPlanStepDraft(
                    capability="system.unknown",
                ),
            ),
        )
    )

    assert result.valid is False
    assert result.issues[0].code == "unknown_capability"
    assert result.issues[0].step_index == 1
