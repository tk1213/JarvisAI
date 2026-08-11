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
            "tests/test_memory_coordination.py",
            "tests/test_memory_coordination_context_assembly.py",
            "tests/test_memory_coordination_safety_hotfix.py",
            "tests/test_memory_coordination_hotfix2.py",
            "tests/test_conversation_production_context.py",
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
    print("Sprint 4.7 Pack B hotfix 2 gate: PASS")


if __name__ == "__main__":
    main()
