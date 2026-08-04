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
        "Sprint 4.0 Pack E static quality gate: PASS"
    )


if __name__ == "__main__":
    main()
