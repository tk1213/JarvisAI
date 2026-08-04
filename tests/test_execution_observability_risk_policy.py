import pytest

from jarvis.planner.risk import (
    PlanRiskLevel,
    PlanRiskPolicy,
)


@pytest.mark.parametrize(
    "capability",
    [
        "system.execution_history",
        "system.execution_detail",
        "system.execution_diagnostics",
    ],
)
def test_execution_observability_capabilities_are_read_only(
    capability: str,
) -> None:
    assert (
        PlanRiskPolicy.classify(
            capability
        )
        is PlanRiskLevel.READ_ONLY
    )


@pytest.mark.parametrize(
    "capability",
    [
        "smart_home.turn_on",
        "smart_home.turn_off",
        "smart_home.toggle",
    ],
)
def test_smart_home_side_effects_remain_side_effects(
    capability: str,
) -> None:
    assert (
        PlanRiskPolicy.classify(
            capability
        )
        is PlanRiskLevel.SIDE_EFFECT
    )
