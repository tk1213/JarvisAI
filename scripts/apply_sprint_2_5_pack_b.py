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


def require_once(
    text: str,
    needle: str,
) -> None:
    count = text.count(needle)

    if count != 1:
        raise RuntimeError(
            f"Expected exactly one occurrence of {needle!r}; "
            f"found {count}."
        )


def main() -> None:
    original = FACTORY_PATH.read_text(
        encoding="utf-8"
    )

    backup = FACTORY_PATH.with_suffix(
        ".py.pack_b_backup"
    )

    shutil.copy2(
        FACTORY_PATH,
        backup,
    )

    updated = original

    import_anchor = (
        "from jarvis.database.db import DatabaseManager\n"
    )

    require_once(
        updated,
        import_anchor,
    )

    memory_imports = (
        "from jarvis.memory.aware_conversation import (\n"
        "    MemoryAwareConversationManager,\n"
        ")\n"
        "from jarvis.memory.capture import MemoryCaptureService\n"
        "from jarvis.memory.extractor import MemoryExtractor\n"
        "from jarvis.memory.repository import MemoryRepository\n"
        "from jarvis.memory.service import (\n"
        "    MemoryService as LongTermMemoryService,\n"
        ")\n"
    )

    updated = updated.replace(
        import_anchor,
        import_anchor + memory_imports,
        1,
    )

    conversation_anchor = (
        "        conversation_manager = ConversationManager(\n"
        "            ai=ai_service,\n"
        "            memory=memory_service,\n"
        "            router=tool_router,\n"
        "            smart_home=smart_home_service,\n"
        "        )\n"
    )

    require_once(
        updated,
        conversation_anchor,
    )

    replacement = (
        "        long_term_repository = MemoryRepository(\n"
        "            database\n"
        "        )\n"
        "\n"
        "        long_term_memory = LongTermMemoryService(\n"
        "            long_term_repository\n"
        "        )\n"
        "\n"
        "        memory_extractor = MemoryExtractor()\n"
        "\n"
        "        memory_capture = MemoryCaptureService(\n"
        "            extractor=memory_extractor,\n"
        "            memory=long_term_memory,\n"
        "        )\n"
        "\n"
        "        conversation_manager = (\n"
        "            MemoryAwareConversationManager(\n"
        "                ai=ai_service,\n"
        "                memory=memory_service,\n"
        "                router=tool_router,\n"
        "                smart_home=smart_home_service,\n"
        "                memory_capture=memory_capture,\n"
        "            )\n"
        "        )\n"
    )

    updated = updated.replace(
        conversation_anchor,
        replacement,
        1,
    )

    register_anchor = (
        "        self.container.register(\n"
        '            "conversation",\n'
        "            conversation_manager,\n"
        "            overwrite=False,\n"
        "        )\n"
    )

    require_once(
        updated,
        register_anchor,
    )

    extra_registrations = (
        "\n"
        "        self.container.register(\n"
        '            "long_term_memory_repository",\n'
        "            long_term_repository,\n"
        "            overwrite=False,\n"
        "        )\n"
        "        self.container.register(\n"
        '            "long_term_memory",\n'
        "            long_term_memory,\n"
        "            overwrite=False,\n"
        "        )\n"
        "        self.container.register(\n"
        '            "memory_extractor",\n'
        "            memory_extractor,\n"
        "            overwrite=False,\n"
        "        )\n"
        "        self.container.register(\n"
        '            "memory_capture",\n'
        "            memory_capture,\n"
        "            overwrite=False,\n"
        "        )\n"
    )

    updated = updated.replace(
        register_anchor,
        register_anchor + extra_registrations,
        1,
    )

    updated = updated.replace(
        "from jarvis.services.conversation_manager "
        "import ConversationManager\n",
        "",
    )

    FACTORY_PATH.write_text(
        updated,
        encoding="utf-8",
    )

    print(
        "Pack B applied successfully."
    )
    print(
        f"Backup created: {backup}"
    )


if __name__ == "__main__":
    main()
