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
        "Focused Sprint 6 Regression",
        [
            sys.executable,
            "-m",
            "pytest",
            "tests/test_assistant_runtime_wake_transition.py",
            "tests/test_continuous_assistant_runtime.py",
            "tests/test_voice_reply_guard.py",
            "tests/test_stt_prompt_echo_guard.py",
            "tests/test_wake_activation_boundary.py",
            "tests/test_wake_command_transition.py",
            "tests/test_wake_command_transition_hotfix.py",
            "tests/test_wake_full_turn.py",
            "tests/test_wake_timing.py",
            "tests/test_wake_word_service_audio.py",
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
        print("=" * 60)
        print(name)
        print("=" * 60)

        completed = subprocess.run(
            command,
            check=False,
        )

        if completed.returncode != 0:
            print()
            print(
                f"Sprint 6 closeout failed at: {name}"
            )

            raise SystemExit(
                completed.returncode
            )

    print()
    print("=" * 60)
    print("SPRINT 6 CLOSEOUT")
    print("=" * 60)
    print()
    print("Compile: PASS")
    print("Ruff: PASS")
    print("Focused Sprint 6 regression: PASS")
    print("Full regression: PASS")
    print()
    print("Sprint 6 closeout gate: PASS")


if __name__ == "__main__":
    main()