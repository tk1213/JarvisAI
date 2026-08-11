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
            "scripts",
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
            "scripts",
        ],
    ),
    (
        "Pytest",
        [
            "pytest",
        ],
    ),
)


def main() -> None:
    for name, command in COMMANDS:
        print()
        print(
            f"=== {name} ==="
        )

        completed = subprocess.run(
            command,
            check=False,
        )

        if completed.returncode != 0:
            raise SystemExit(
                completed.returncode
            )

    print()
    print(
        "Sprint 4.1 Pack A static quality gate: PASS"
    )


if __name__ == "__main__":
    main()
