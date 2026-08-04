from __future__ import annotations

from jarvis.planner.service import PlannerService
from jarvis.services.capability import CapabilityRequest


class DemoRegistry:
    def is_allowed(
        self,
        capability: str,
    ) -> bool:
        return capability in {
            "smart_home.turn_off",
            "smart_home.status",
        }


def main() -> None:
    planner = PlannerService(
        DemoRegistry(),  # type: ignore[arg-type]
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

    print(
        f"Goal: {plan.goal}"
    )
    print(
        f"Status: {plan.status.value}"
    )

    for step in plan.steps:
        print(
            f"{step.index}. "
            f"{step.capability} "
            f"{step.arguments}"
        )


if __name__ == "__main__":
    main()
