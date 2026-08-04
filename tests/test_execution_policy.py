from jarvis.planner.execution_policy import ExecutionPolicy, ExecutionRoute
from jarvis.planner.models import Plan, PlanStatus, PlanStep


def test_read_only_plan_does_not_require_confirmation() -> None:
    plan = Plan(
        goal="Check system and device status",
        steps=[
            PlanStep(index=1, capability="system.health"),
            PlanStep(index=2, capability="smart_home.status"),
        ],
        status=PlanStatus.READY,
    )

    decision = ExecutionPolicy().evaluate(plan)

    assert decision.route is ExecutionRoute.READ_ONLY
    assert decision.requires_confirmation is False
    assert decision.side_effect_steps == ()


def test_mixed_plan_requires_confirmation() -> None:
    plan = Plan(
        goal="Turn off device and verify status",
        steps=[
            PlanStep(index=1, capability="smart_home.turn_off"),
            PlanStep(index=2, capability="smart_home.status"),
        ],
        status=PlanStatus.READY,
    )

    decision = ExecutionPolicy().evaluate(plan)

    assert (
        decision.route
        is ExecutionRoute.CONFIRMATION_REQUIRED
    )
    assert decision.requires_confirmation is True
    assert decision.side_effect_steps == (1,)


def test_toggle_plan_requires_confirmation() -> None:
    plan = Plan(
        goal="Toggle device",
        steps=[
            PlanStep(index=1, capability="smart_home.toggle"),
        ],
        status=PlanStatus.READY,
    )

    decision = ExecutionPolicy().evaluate(plan)

    assert decision.requires_confirmation is True
