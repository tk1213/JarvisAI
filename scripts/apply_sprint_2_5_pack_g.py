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


def require(
    text: str,
    needle: str,
) -> None:
    if needle not in text:
        raise RuntimeError(
            f"Required anchor not found: {needle!r}"
        )


def main() -> None:
    original = FACTORY_PATH.read_text(
        encoding="utf-8"
    )

    backup = FACTORY_PATH.with_suffix(
        ".py.pack_g_backup"
    )
    shutil.copy2(
        FACTORY_PATH,
        backup,
    )

    updated = original

    capture_import = (
        "from jarvis.memory.capture import "
        "MemoryCaptureService\n"
    )
    commands_import = (
        "from jarvis.memory.commands import "
        "MemoryCommandService\n"
    )

    require(
        updated,
        capture_import,
    )

    if commands_import not in updated:
        updated = updated.replace(
            capture_import,
            capture_import + commands_import,
            1,
        )

    extractor_block = (
        "        memory_extractor = MemoryExtractor()\n"
    )

    require(
        updated,
        extractor_block,
    )

    commands_block = (
        "\n"
        "        memory_commands = MemoryCommandService(\n"
        "            memory=long_term_memory,\n"
        "            extractor=memory_extractor,\n"
        "        )\n"
    )

    if "memory_commands = MemoryCommandService(" not in updated:
        updated = updated.replace(
            extractor_block,
            extractor_block + commands_block,
            1,
        )

    manager_anchor = (
        "                memory_context=memory_context,\n"
        "            )\n"
    )

    require(
        updated,
        manager_anchor,
    )

    manager_replacement = (
        "                memory_context=memory_context,\n"
        "                memory_commands=memory_commands,\n"
        "            )\n"
    )

    if "memory_commands=memory_commands" not in updated:
        updated = updated.replace(
            manager_anchor,
            manager_replacement,
            1,
        )

    context_registration = (
        "        self.container.register(\n"
        '            "memory_context",\n'
        "            memory_context,\n"
        "            overwrite=False,\n"
        "        )\n"
    )

    require(
        updated,
        context_registration,
    )

    commands_registration = (
        "\n"
        "        self.container.register(\n"
        '            "memory_commands",\n'
        "            memory_commands,\n"
        "            overwrite=False,\n"
        "        )\n"
    )

    if '"memory_commands"' not in updated:
        updated = updated.replace(
            context_registration,
            context_registration
            + commands_registration,
            1,
        )

    FACTORY_PATH.write_text(
        updated,
        encoding="utf-8",
    )

    print(
        "Sprint 2.5 Pack G applied successfully."
    )
    print(
        f"Backup created: {backup}"
    )


if __name__ == "__main__":
    main()
