import pytest

from jarvis.planner.models import PlanStatus
from jarvis.planner.service import PlannerService
from jarvis.services.capability import CapabilityRequest


class StubRegistry:
    def __init__(
        self,
        allowed: set[str],
    ) -> None:
        self._allowed = allowed

    def is_allowed(
        self,
        capability: str,
    ) -> bool:
        return capability in self._allowed


def test_create_single_step_plan() -> None:
    registry = StubRegistry(
        {
            "system.ping",
        }
    )

    planner = PlannerService(
        registry,  # type: ignore[arg-type]
    )

    plan = planner.create_single_step_plan(
        goal="Check Jarvis",
        request=CapabilityRequest(
            capability="system.ping",
            arguments={},
        ),
    )

    assert plan.status is PlanStatus.READY
    assert plan.goal == "Check Jarvis"
    assert plan.steps[0].capability == "system.ping"


def test_create_multi_step_plan() -> None:
    registry = StubRegistry(
        {
            "smart_home.turn_off",
            "smart_home.status",
        }
    )

    planner = PlannerService(
        registry,  # type: ignore[arg-type]
    )

    plan = planner.create_plan(
        goal="Turn off bedroom light and check status",
        requests=[
            CapabilityRequest(
                capability="smart_home.turn_off",
                arguments={
                    "device": "bedroom light",
                },
            ),
            CapabilityRequest(
                capability="smart_home.status",
                arguments={
                    "device": "bedroom light",
                },
            ),
        ],
    )

    assert [
        step.index
        for step in plan.steps
    ] == [1, 2]

    assert [
        step.capability
        for step in plan.steps
    ] == [
        "smart_home.turn_off",
        "smart_home.status",
    ]


def test_disallowed_capability_is_rejected() -> None:
    registry = StubRegistry(
        {
            "system.ping",
        }
    )

    planner = PlannerService(
        registry,  # type: ignore[arg-type]
    )

    with pytest.raises(
        PermissionError,
        match="not allowed",
    ):
        planner.create_single_step_plan(
            goal="Do something unsafe",
            request=CapabilityRequest(
                capability="unknown.capability",
                arguments={},
            ),
        )


def test_empty_request_list_is_rejected() -> None:
    registry = StubRegistry(
        {
            "system.ping",
        }
    )

    planner = PlannerService(
        registry,  # type: ignore[arg-type]
    )

    with pytest.raises(
        ValueError,
        match="at least one",
    ):
        planner.create_plan(
            goal="Nothing",
            requests=[],
        )
