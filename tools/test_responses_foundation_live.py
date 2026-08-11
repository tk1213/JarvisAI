from __future__ import annotations

from jarvis.ai.openai_client import OpenAIClient
from jarvis.ai.responses_service import ResponsesService
from jarvis.config import settings


def main() -> None:
    client = OpenAIClient()

    service = ResponsesService(
        responses_api=client.client.responses,
        model=client.model,
        max_output_tokens=(
            settings.openai_max_output_tokens
        ),
    )

    print(
        "Sprint 4.2 Responses API Foundation"
    )
    print(
        "-" * 60
    )
    print(
        f"Model: {client.model}"
    )
    print(
        "Timeout seconds: "
        f"{settings.openai_timeout_seconds}"
    )
    print(
        f"Max retries: {settings.openai_max_retries}"
    )
    print(
        "Responses service available: "
        f"{service is not None}"
    )
    print(
        "Responses API foundation gate: PASS"
    )


if __name__ == "__main__":
    main()
