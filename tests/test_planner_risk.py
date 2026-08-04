from jarvis.planner.risk import PlanRiskLevel, PlanRiskPolicy


def test_status_is_read_only() -> None:
    assert (
        PlanRiskPolicy.classify("smart_home.status")
        is PlanRiskLevel.READ_ONLY
    )


def test_list_devices_is_read_only() -> None:
    assert (
        PlanRiskPolicy.classify("smart_home.list_devices")
        is PlanRiskLevel.READ_ONLY
    )


def test_turn_off_is_side_effect() -> None:
    assert (
        PlanRiskPolicy.classify("smart_home.turn_off")
        is PlanRiskLevel.SIDE_EFFECT
    )


def test_toggle_is_side_effect() -> None:
    assert (
        PlanRiskPolicy.classify("smart_home.toggle")
        is PlanRiskLevel.SIDE_EFFECT
    )


def test_unknown_capability_defaults_to_side_effect() -> None:
    assert (
        PlanRiskPolicy.classify("future.unknown_action")
        is PlanRiskLevel.SIDE_EFFECT
    )
