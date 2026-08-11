from __future__ import annotations

from pathlib import Path


SETTINGS_PATH = Path(
    "src/jarvis/config/settings.py"
)

OPENAI_CLIENT_PATH = Path(
    "src/jarvis/ai/openai_client.py"
)


def patch_settings(text: str) -> str:
    anchor = (
        '    openai_model: str = "gpt-5.5"\n'
    )

    insert = (
        anchor
        + "\n"
        + "    openai_timeout_seconds: float = 60.0\n"
        + "    openai_max_retries: int = 2\n"
        + "    openai_max_output_tokens: int | None = None\n"
    )

    if "openai_timeout_seconds:" not in text:
        if anchor not in text:
            raise SystemExit(
                "OpenAI settings anchor was not found."
            )

        text = text.replace(
            anchor,
            insert,
            1,
        )

    return text


def patch_openai_client(text: str) -> str:
    old = (
        "        self.client = AsyncOpenAI(\n"
        "            api_key=api_key,\n"
        "            timeout=60.0,\n"
        "            max_retries=2,\n"
        "        )\n"
    )

    new = (
        "        self.client = AsyncOpenAI(\n"
        "            api_key=api_key,\n"
        "            timeout=settings.openai_timeout_seconds,\n"
        "            max_retries=settings.openai_max_retries,\n"
        "        )\n"
    )

    if old in text:
        text = text.replace(
            old,
            new,
            1,
        )
    elif (
        "timeout=settings.openai_timeout_seconds"
        not in text
    ):
        raise SystemExit(
            "OpenAI client configuration anchor was not found."
        )

    return text


def main() -> None:
    settings_text = SETTINGS_PATH.read_text(
        encoding="utf-8"
    )
    client_text = OPENAI_CLIENT_PATH.read_text(
        encoding="utf-8"
    )

    SETTINGS_PATH.write_text(
        patch_settings(settings_text),
        encoding="utf-8",
    )

    OPENAI_CLIENT_PATH.write_text(
        patch_openai_client(client_text),
        encoding="utf-8",
    )

    print(
        "Sprint 4.2 Pack A Responses API hardening applied."
    )


if __name__ == "__main__":
    main()
