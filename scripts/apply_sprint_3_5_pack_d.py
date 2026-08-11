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
        ".py.sprint_3_5_pack_d_backup"
    )

    shutil.copy2(
        APPLICATION,
        backup,
    )

    executor_import = (
        "from jarvis.planner.executor import PlanExecutor\n"
    )

    persistence_imports = (
        "from jarvis.planner.execution_persistence import (\n"
        "    ExecutionPersistenceService,\n"
        ")\n"
        "from jarvis.planner.execution_repository import (\n"
        "    PlanExecutionRepository,\n"
        ")\n"
        "from jarvis.planner.persisting_executor import (\n"
        "    PersistingPlanExecutor,\n"
        ")\n"
    )

    if persistence_imports not in text:
        require_once(
            text,
            executor_import,
        )

        text = text.replace(
            executor_import,
            executor_import + persistence_imports,
            1,
        )

    old_executor = (
        "            plan_executor = PlanExecutor(\n"
        "                capability_router\n"
        "            )\n"
    )

    new_executor = (
        "            execution_repository = PlanExecutionRepository(\n"
        "                database\n"
        "            )\n"
        "\n"
        "            execution_persistence = ExecutionPersistenceService(\n"
        "                execution_repository\n"
        "            )\n"
        "\n"
        "            plan_executor = PersistingPlanExecutor(\n"
        "                capability_router,\n"
        "                persistence=execution_persistence,\n"
        "            )\n"
    )

    if "PersistingPlanExecutor(" not in text:
        require_once(
            text,
            old_executor,
        )

        text = text.replace(
            old_executor,
            new_executor,
            1,
        )

    registration_anchor = (
        "            container.register(\n"
        '                "plan_executor",\n'
        "                plan_executor,\n"
        "                overwrite=False,\n"
        "            )\n"
    )

    registration = (
        "\n"
        "            container.register(\n"
        '                "execution_repository",\n'
        "                execution_repository,\n"
        "                overwrite=False,\n"
        "            )\n"
        "\n"
        "            container.register(\n"
        '                "execution_persistence",\n'
        "                execution_persistence,\n"
        "                overwrite=False,\n"
        "            )\n"
    )

    if '"execution_persistence"' not in text:
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
        "Sprint 3.5 Pack D applied successfully."
    )
    print(
        f"Backup: {backup}"
    )


if __name__ == "__main__":
    main()
