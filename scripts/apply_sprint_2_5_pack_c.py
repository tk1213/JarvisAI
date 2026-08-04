from __future__ import annotations

from pathlib import Path
import shutil


PROJECT_ROOT = Path(__file__).resolve().parents[1]
FACTORY_PATH = (
    PROJECT_ROOT
    / "src"
    / "jarvis"
    / "core"
    / "service_factory.py"
)


def main() -> None:
    original = FACTORY_PATH.read_text(
        encoding="utf-8"
    )

    backup = FACTORY_PATH.with_suffix(
        ".py.pack_c_backup"
    )

    shutil.copy2(
        FACTORY_PATH,
        backup,
    )

    updated = original

    capture_import = (
        "from jarvis.memory.capture import "
        "MemoryCaptureService\\n"
    )

    context_import = (
        "from jarvis.memory.context import "
        "MemoryContextBuilder\\n"
    )

    if context_import not in updated:
        updated = updated.replace(
            capture_import,
            capture_import + context_import,
            1,
        )

    capture_block = (
        "        memory_capture = MemoryCaptureService(\\n"
        "            extractor=memory_extractor,\\n"
        "            memory=long_term_memory,\\n"
        "        )\\n"
    )

    context_block = (
        "\\n"
        "        memory_context = MemoryContextBuilder(\\n"
        "            long_term_memory\\n"
        "        )\\n"
    )

    if "memory_context = MemoryContextBuilder(" not in updated:
        updated = updated.replace(
            capture_block,
            capture_block + context_block,
            1,
        )

    manager_old = (
        "                memory_capture=memory_capture,\\n"
        "            )\\n"
    )

    manager_new = (
        "                memory_capture=memory_capture,\\n"
        "                memory_context=memory_context,\\n"
        "            )\\n"
    )

    if "memory_context=memory_context" not in updated:
        updated = updated.replace(
            manager_old,
            manager_new,
            1,
        )

    register_capture = (
        "        self.container.register(\\n"
        '            "memory_capture",\\n'
        "            memory_capture,\\n"
        "            overwrite=False,\\n"
        "        )\\n"
    )

    register_context = (
        "\\n"
        "        self.container.register(\\n"
        '            "memory_context",\\n'
        "            memory_context,\\n"
        "            overwrite=False,\\n"
        "        )\\n"
    )

    if '"memory_context"' not in updated:
        updated = updated.replace(
            register_capture,
            register_capture + register_context,
            1,
        )

    FACTORY_PATH.write_text(
        updated,
        encoding="utf-8",
    )

    print("Pack C applied successfully.")
    print(f"Backup: {backup}")


if __name__ == "__main__":
    main()
