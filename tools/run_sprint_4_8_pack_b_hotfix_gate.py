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
        "Focused Pytest",
        [
            sys.executable,
            "-m",
            "pytest",
            "tests/test_conversation_recovery_execution.py",
            "tests/test_conversation_recovery_execution_integration.py",
            "tests/test_conversation_recovery_integration.py",
            "tests/test_conversation_recovery_execution_semantics_hotfix.py",
            "-q",
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
    print("Sprint 4.8 Pack B hotfix gate: PASS")


if __name__ == "__main__":
    main()
