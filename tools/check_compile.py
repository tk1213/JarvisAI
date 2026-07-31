from __future__ import annotations

import pathlib
import py_compile
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

SEARCH_DIRS = [
    ROOT / "src",
    ROOT / "tests",
    ROOT / "tools",
]


def iter_python_files():
    for directory in SEARCH_DIRS:
        if not directory.exists():
            continue

        yield from directory.rglob("*.py")


def main() -> int:
    print("=" * 60)
    print(" JarvisAI Compile Check")
    print("=" * 60)

    total = 0
    passed = 0
    failed = []

    for file in iter_python_files():
        total += 1

        try:
            py_compile.compile(
                str(file),
                doraise=True,
            )

            print(f"[ OK ] {file.relative_to(ROOT)}")
            passed += 1

        except py_compile.PyCompileError as exc:
            print(f"[FAIL] {file.relative_to(ROOT)}")
            print(exc.msg)
            failed.append(file)

    print("\n" + "=" * 60)
    print(f"Total  : {total}")
    print(f"Passed : {passed}")
    print(f"Failed : {len(failed)}")
    print("=" * 60)

    if failed:
        print("\nFiles with errors:")

        for file in failed:
            print(f" - {file.relative_to(ROOT)}")

        return 1

    print("\n✅ All Python files compiled successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())