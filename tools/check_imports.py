from __future__ import annotations

import importlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "src"


def iter_modules():
    for file in SRC.rglob("*.py"):
        if file.name == "__init__.py":
            continue

        relative = file.relative_to(SRC)
        module = ".".join(relative.with_suffix("").parts)

        yield module


def main() -> int:
    print("=" * 60)
    print(" JarvisAI Import Check")
    print("=" * 60)

    sys.path.insert(0, str(SRC))

    total = 0
    failed = []

    for module in sorted(iter_modules()):
        total += 1

        try:
            importlib.import_module(module)
            print(f"[ OK ] {module}")

        except Exception as exc:  # noqa: BLE001
            print(f"[FAIL] {module}")
            print(f"       {type(exc).__name__}: {exc}")
            failed.append(module)

    print("\n" + "=" * 60)
    print(f"Total  : {total}")
    print(f"Passed : {total - len(failed)}")
    print(f"Failed : {len(failed)}")
    print("=" * 60)

    if failed:
        print("\nModules with errors:")

        for module in failed:
            print(f" - {module}")

        return 1

    print("\n✅ All modules imported successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())