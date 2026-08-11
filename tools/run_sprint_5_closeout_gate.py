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
        "Audio Device Live Gate",
        [
            sys.executable,
            "tools/test_audio_manager_selection_live.py",
        ],
    ),
    (
        "Microphone Signal Live Gate",
        [
            sys.executable,
            "tools/test_microphone_signal_live.py",
        ],
    ),
    (
        "Microphone STT Live Gate",
        [
            sys.executable,
            "tools/test_microphone_stt_live.py",
        ],
    ),
    (
        "VAD Live Gate",
        [
            sys.executable,
            "tools/test_vad_recording_live.py",
        ],
    ),
    (
        "Voice Wiring Live Gate",
        [
            sys.executable,
            "tools/test_voice_wiring_live.py",
        ],
    ),
    (
        "Real Voice Turn Live Gate",
        [
            sys.executable,
            "tools/test_real_voice_turn_live.py",
        ],
    ),
    (
        "Voice Follow-up Live Gate",
        [
            sys.executable,
            "tools/test_real_voice_followup_live.py",
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
    print("Sprint 5 closeout gate: PASS")
    print("Production Voice Runtime: COMPLETE")


if __name__ == "__main__":
    main()
