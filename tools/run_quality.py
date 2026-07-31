from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def run(title: str, command: list[str]) -> bool:
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)

    result = subprocess.run(command, cwd=ROOT, check=False)

    if result.returncode == 0:
        print(f"[PASS] {title}")
        return True

    print(f"[FAIL] {title}")
    return False


def main() -> int:
    checks = [
        (
            "Compile Check",
            [sys.executable, "tools/check_compile.py"],
        ),
        (
            "Import Check",
            [sys.executable, "tools/check_imports.py"],
        ),
        (
            "Ruff",
            [
                sys.executable,
                "-m",
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
                sys.executable,
                "-m",
                "pytest",
            ],
        ),
    ]

    results: list[bool] = []

    for title, command in checks:
        results.append(run(title, command))

    print()
    print("=" * 70)
    print("QUALITY SUMMARY")
    print("=" * 70)

    passed = sum(results)
    total = len(results)

    print(f"Passed : {passed}/{total}")

    if passed == total:
        print("🎉 All quality checks passed.")
        return 0

    print("❌ Some quality checks failed.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())