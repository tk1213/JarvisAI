from __future__ import annotations

import shutil
from pathlib import Path

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
        ".py.pack_d_backup"
    )

    shutil.copy2(
        FACTORY_PATH,
        backup,
    )

    updated = original

    context_import = (
        "from jarvis.memory.context import "
        "MemoryContextBuilder\n"
    )

    retriever_import = (
        "from jarvis.memory.retriever import "
        "MemoryRetriever\n"
    )

    if retriever_import not in updated:
        updated = updated.replace(
            context_import,
            context_import + retriever_import,
            1,
        )

    old_context = (
        "        memory_context = MemoryContextBuilder(\n"
        "            long_term_memory\n"
        "        )\n"
    )

    new_context = (
        "        memory_retriever = MemoryRetriever(\n"
        "            long_term_memory\n"
        "        )\n"
        "\n"
        "        memory_context = MemoryContextBuilder(\n"
        "            memory_retriever\n"
        "        )\n"
    )

    if (
        "memory_retriever = MemoryRetriever("
        not in updated
    ):
        updated = updated.replace(
            old_context,
            new_context,
            1,
        )

    context_registration = (
        "        self.container.register(\n"
        '            "memory_context",\n'
        "            memory_context,\n"
        "            overwrite=False,\n"
        "        )\n"
    )

    retriever_registration = (
        "        self.container.register(\n"
        '            "memory_retriever",\n'
        "            memory_retriever,\n"
        "            overwrite=False,\n"
        "        )\n"
        "\n"
    )

    if '"memory_retriever"' not in updated:
        updated = updated.replace(
            context_registration,
            retriever_registration
            + context_registration,
            1,
        )

    FACTORY_PATH.write_text(
        updated,
        encoding="utf-8",
    )

    print(
        "Sprint 2.5 Pack D applied successfully."
    )
    print(
        f"Backup created: {backup}"
    )


if __name__ == "__main__":
    main()
