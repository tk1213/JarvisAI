from __future__ import annotations

from jarvis.planner.risk import (
    PlanRiskLevel,
    PlanRiskPolicy,
)


def main() -> None:
    read_only = (
        "system.execution_statistics",
        "system.capability_reliability",
        "system.execution_health",
        "system.execution_health_trend",
    )

    side_effects = (
        "smart_home.turn_on",
        "smart_home.turn_off",
        "smart_home.toggle",
    )

    print(
        "Sprint 3.7 Execution Analytics Risk Policy"
    )
    print(
        "-" * 60
    )

    for capability in read_only:
        risk = PlanRiskPolicy.classify(
            capability
        )

        print(
            f"{capability}: {risk.value}"
        )

        if risk is not PlanRiskLevel.READ_ONLY:
            raise RuntimeError(
                f"{capability} must be read-only."
            )

    for capability in side_effects:
        risk = PlanRiskPolicy.classify(
            capability
        )

        print(
            f"{capability}: {risk.value}"
        )

        if risk is not PlanRiskLevel.SIDE_EFFECT:
            raise RuntimeError(
                f"{capability} must remain side-effect."
            )

    print(
        "Execution analytics risk policy gate: PASS"
    )


if __name__ == "__main__":
    main()
