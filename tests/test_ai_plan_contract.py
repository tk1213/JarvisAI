import pytest

from jarvis.planner.ai_plan_contract import (
    AIPlanDraft,
    AIPlanStepDraft,
)


def test_ai_plan_contract_normalizes_values() -> None:
    draft = AIPlanDraft(
        goal="  Check system health  ",
        steps=(
            AIPlanStepDraft(
                capability=" system.health ",
                description=" Check health ",
            ),
        ),
        reasoning_summary=" Read-only check ",
    )

    assert draft.goal == "Check system health"
    assert draft.steps[0].capability == "system.health"
    assert draft.steps[0].description == "Check health"
    assert draft.reasoning_summary == "Read-only check"


def test_ai_plan_contract_rejects_empty_steps() -> None:
    with pytest.raises(
        ValueError,
        match="at least one step",
    ):
        AIPlanDraft(
            goal="Health",
            steps=(),
        )
