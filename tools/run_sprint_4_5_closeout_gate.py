from __future__ import annotations

import subprocess
import sys

COMMANDS = (
    (
        "Compile",
        [
            sys.executable,
            "-m",
            "compileall",
            "-q",
            "src",
            "tests",
            "tools",
        ],
    ),
    (
        "Ruff",
        [
            "ruff",
            "check",
            "src",
            "tests",
            "tools",
        ],
    ),
    (
        "Full Pytest",
        [
            sys.executable,
            "-m",
            "pytest",
            "-q",
        ],
    ),
    (
        "Pack A Live Gate",
        [
            sys.executable,
            "tools/test_conversation_turn_live.py",
        ],
    ),
    (
        "Pack B Hotfix Live Gate",
        [
            sys.executable,
            "tools/test_conversation_turn_integration_hotfix_live.py",
        ],
    ),
    (
        "Pack C Live Gate",
        [
            sys.executable,
            "tools/test_conversation_route_attribution_live.py",
        ],
    ),
    (
        "Pack D Live Gate",
        [
            sys.executable,
            "tools/test_conversation_turn_tracing_live.py",
        ],
    ),
)


def main() -> None:
    for name, command in COMMANDS:
        print()
        print(f"=== {name} ===")

        completed = subprocess.run(
            command,
            check=False,
        )

        if completed.returncode != 0:
            raise SystemExit(
                completed.returncode
            )

    print()
    print("Sprint 4.5 closeout gate: PASS")


if __name__ == "__main__":
    main()
