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
            "tools/test_durable_agent_memory_live.py",
        ],
    ),
    (
        "Pack B Live Gate",
        [
            sys.executable,
            "tools/test_agent_memory_startup_live.py",
        ],
    ),
    (
        "Pack C Live Gate",
        [
            sys.executable,
            "tools/test_memory_coordination_live.py",
        ],
    ),
    (
        "Pack D Live Gate",
        [
            sys.executable,
            "tools/test_agent_memory_retention_live.py",
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
    print("Sprint 4.4 closeout gate: PASS")


if __name__ == "__main__":
    main()
