from __future__ import annotations

from jarvis.planner.compensation import (
    CompensationCandidate,
    CompensationPlan,
    CompensationStatus,
)
from jarvis.planner.recovery_policy import RecoveryPolicy


def main() -> None:
    compensation = CompensationPlan(
        status=CompensationStatus.REQUIRES_REVIEW,
        candidates=(
            CompensationCandidate(
                step_index=2,
                capability="smart_home.turn_off",
                arguments={
                    "device_query": "Demo Plug",
                },
            ),
        ),
        reason=(
            "A side-effect step completed before failure."
        ),
    )

    decision = RecoveryPolicy().decide(
        compensation
    )

    print(
        "Sprint 3.3 Recovery Policy"
    )
    print(
        "-" * 60
    )
    print(
        f"Decision: {decision.decision.value}"
    )
    print(
        "Requires manual review: "
        f"{decision.requires_manual_review}"
    )

    for candidate in decision.candidates:
        print(
            f"Candidate: step={candidate.step_index} "
            f"capability={candidate.capability}"
        )

    if not decision.requires_manual_review:
        raise RuntimeError(
            "Recovery policy gate failed."
        )

    print(
        "Recovery policy gate: PASS"
    )


if __name__ == "__main__":
    main()
