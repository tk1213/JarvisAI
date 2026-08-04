import pytest

from jarvis.planner.ai_plan_adapter import (
    AIPlanAdaptationError,
    AIPlanAdapter,
)
from jarvis.planner.ai_plan_parser import AIPlanParser
from jarvis.planner.ai_plan_pipeline import AIPlanPipeline
from jarvis.planner.ai_plan_validation import AIPlanValidator
from jarvis.planner.service import PlannerService
from jarvis.services.capability import CapabilityDefinition
from jarvis.services.capability_registry import CapabilityRegistry


def make_pipeline() -> AIPlanPipeline:
    registry = CapabilityRegistry(
        [
            CapabilityDefinition(
                name="system.ping",
            ),
        ]
    )

    return AIPlanPipeline(
        parser=AIPlanParser(),
        adapter=AIPlanAdapter(
            validator=AIPlanValidator(
                registry
            ),
            planner=PlannerService(
                registry
            ),
        ),
    )


def test_pipeline_parses_validates_and_adapts() -> None:
    result = make_pipeline().build(
        {
            "goal": "Ping Jarvis",
            "steps": [
                {
                    "capability": "system.ping",
                    "arguments": {},
                    "description": "Check responsiveness",
                }
            ],
        }
    )

    assert result.draft.goal == "Ping Jarvis"
    assert result.adaptation.plan.goal == (
        "Ping Jarvis"
    )
    assert result.adaptation.validation.valid is True


def test_pipeline_rejects_invalid_capability() -> None:
    with pytest.raises(
        AIPlanAdaptationError,
        match="unknown capability",
    ):
        make_pipeline().build(
            {
                "goal": "Unknown",
                "steps": [
                    {
                        "capability": "system.unknown",
                        "arguments": {},
                    }
                ],
            }
        )
