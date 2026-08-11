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
        ".py.pack_h_backup"
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

    audit_imports = (
        "from jarvis.memory.audit_repository import (\n"
        "    MemoryAuditRepository,\n"
        ")\n"
        "from jarvis.memory.audit_service import (\n"
        "    MemoryAuditService,\n"
        ")\n"
    )

    require(
        updated,
        capture_import,
    )

    if "MemoryAuditRepository" not in updated:
        updated = updated.replace(
            capture_import,
            audit_imports + capture_import,
            1,
        )

    repository_block = (
        "        long_term_repository = MemoryRepository(\n"
        "            database\n"
        "        )\n"
    )

    require(
        updated,
        repository_block,
    )

    audit_block = (
        "\n"
        "        memory_audit_repository = MemoryAuditRepository(\n"
        "            database\n"
        "        )\n"
        "\n"
        "        memory_audit = MemoryAuditService(\n"
        "            memory_audit_repository\n"
        "        )\n"
    )

    if "memory_audit_repository =" not in updated:
        updated = updated.replace(
            repository_block,
            repository_block + audit_block,
            1,
        )

    old_memory_service = (
        "        long_term_memory = LongTermMemoryService(\n"
        "            long_term_repository\n"
        "        )\n"
    )

    new_memory_service = (
        "        long_term_memory = LongTermMemoryService(\n"
        "            long_term_repository,\n"
        "            audit=memory_audit,\n"
        "        )\n"
    )

    require(
        updated,
        old_memory_service,
    )

    updated = updated.replace(
        old_memory_service,
        new_memory_service,
        1,
    )

    old_capture = (
        "        memory_capture = MemoryCaptureService(\n"
        "            extractor=memory_extractor,\n"
        "            memory=long_term_memory,\n"
        "        )\n"
    )

    new_capture = (
        "        memory_capture = MemoryCaptureService(\n"
        "            extractor=memory_extractor,\n"
        "            memory=long_term_memory,\n"
        "            audit=memory_audit,\n"
        "        )\n"
    )

    require(
        updated,
        old_capture,
    )

    updated = updated.replace(
        old_capture,
        new_capture,
        1,
    )

    registration_anchor = (
        "        self.container.register(\n"
        '            "long_term_memory",\n'
        "            long_term_memory,\n"
        "            overwrite=False,\n"
        "        )\n"
    )

    require(
        updated,
        registration_anchor,
    )

    audit_registration = (
        "\n"
        "        self.container.register(\n"
        '            "memory_audit_repository",\n'
        "            memory_audit_repository,\n"
        "            overwrite=False,\n"
        "        )\n"
        "        self.container.register(\n"
        '            "memory_audit",\n'
        "            memory_audit,\n"
        "            overwrite=False,\n"
        "        )\n"
    )

    if '"memory_audit"' not in updated:
        updated = updated.replace(
            registration_anchor,
            registration_anchor + audit_registration,
            1,
        )

    FACTORY_PATH.write_text(
        updated,
        encoding="utf-8",
    )

    print(
        "Sprint 2.5 Pack H applied successfully."
    )
    print(
        f"Backup created: {backup}"
    )


if __name__ == "__main__":
    main()
