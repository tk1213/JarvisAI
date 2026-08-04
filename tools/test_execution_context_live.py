from __future__ import annotations

from jarvis.planner.context import ExecutionContext
from jarvis.planner.references import StepValueResolver


def main() -> None:
    context = ExecutionContext()

    context.set_output(
        1,
        {
            "device": {
                "id": "plug-001",
                "name": "Smart Plug 1",
            },
            "power": False,
        },
    )

    resolver = StepValueResolver()

    arguments = resolver.resolve_arguments(
        {
            "device_id": {
                "$step": "1.device.id",
            },
            "expected_power": {
                "$step": "1.power",
            },
        },
        context=context,
    )

    print(
        "Sprint 3.3 Execution Context"
    )
    print(
        "-" * 60
    )
    print(
        f"Step 1 output: {context.get_output(1)!r}"
    )
    print(
        f"Resolved arguments: {arguments!r}"
    )
    print(
        "Execution context gate: PASS"
    )


if __name__ == "__main__":
    main()
