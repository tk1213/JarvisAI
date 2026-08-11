from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APPLICATION = (
    ROOT
    / "src"
    / "jarvis"
    / "core"
    / "application.py"
)


def require_once(
    text: str,
    needle: str,
) -> None:
    count = text.count(
        needle
    )

    if count != 1:
        raise RuntimeError(
            "Expected exactly one anchor, "
            f"found {count}: {needle!r}"
        )


def main() -> None:
    text = APPLICATION.read_text(
        encoding="utf-8"
    )

    backup = APPLICATION.with_suffix(
        ".py.sprint_3_4_pack_g_backup"
    )

    shutil.copy2(
        APPLICATION,
        backup,
    )

    import_anchor = (
        "from jarvis.planner.service import PlannerService\n"
    )

    import_block = (
        "from jarvis.planner.resilience_runtime import (\n"
        "    resilience_runtime,\n"
        ")\n"
    )

    if import_block not in text:
        require_once(
            text,
            import_anchor,
        )

        text = text.replace(
            import_anchor,
            import_anchor + import_block,
            1,
        )

    registration_anchor = (
        "            container.register(\n"
        '                "planner_orchestrator",\n'
        "                planner_orchestrator,\n"
        "                overwrite=False,\n"
        "            )\n"
    )

    registration = (
        "\n"
        "            container.register(\n"
        '                "resilience_runtime",\n'
        "                resilience_runtime,\n"
        "                overwrite=False,\n"
        "            )\n"
    )

    if '"resilience_runtime"' not in text:
        require_once(
            text,
            registration_anchor,
        )

        text = text.replace(
            registration_anchor,
            registration_anchor + registration,
            1,
        )

    APPLICATION.write_text(
        text,
        encoding="utf-8",
    )

    print(
        "Sprint 3.4 Pack G applied successfully."
    )
    print(
        f"Backup: {backup}"
    )


if __name__ == "__main__":
    main()
