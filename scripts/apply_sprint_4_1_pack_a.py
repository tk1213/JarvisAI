from __future__ import annotations

from pathlib import Path

APPLICATION_PATH = Path(
    "src/jarvis/core/application.py"
)

IMPORT_ANCHOR = (
    "from jarvis.ai.openai_client import OpenAIClient\n"
)

IMPORT_INSERT = (
    "from jarvis.agent.bootstrap import "
    "register_ai_agent_runtime\n"
)

REGISTER_ANCHOR = (
    "            container.register(\n"
    '                "planner_orchestrator",\n'
    "                planner_orchestrator,\n"
    "                overwrite=False,\n"
    "            )\n"
)

REGISTER_INSERT = (
    REGISTER_ANCHOR
    + "\n"
    + "            register_ai_agent_runtime(\n"
    + "                container,\n"
    + "                overwrite=False,\n"
    + "            )\n"
)


def main() -> None:
    if not APPLICATION_PATH.exists():
        raise SystemExit(
            f"Missing file: {APPLICATION_PATH}"
        )

    text = APPLICATION_PATH.read_text(
        encoding="utf-8"
    )

    if IMPORT_INSERT not in text:
        if IMPORT_ANCHOR not in text:
            raise SystemExit(
                "Import anchor was not found."
            )

        text = text.replace(
            IMPORT_ANCHOR,
            IMPORT_ANCHOR + IMPORT_INSERT,
            1,
        )

    if (
        "register_ai_agent_runtime("
        not in text
    ):
        if REGISTER_ANCHOR not in text:
            raise SystemExit(
                "Planner orchestrator registration "
                "anchor was not found."
            )

        text = text.replace(
            REGISTER_ANCHOR,
            REGISTER_INSERT,
            1,
        )

    APPLICATION_PATH.write_text(
        text,
        encoding="utf-8",
    )

    print(
        "Sprint 4.1 Pack A application integration applied."
    )


if __name__ == "__main__":
    main()
