from __future__ import annotations

import asyncio
from types import SimpleNamespace

from jarvis.ai.responses_service import ResponsesService


class FakeResponsesAPI:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    async def create(
        self,
        **kwargs,
    ):
        self.calls.append(
            dict(kwargs)
        )

        if len(self.calls) == 1:
            return SimpleNamespace(
                id="resp-1",
                model="test-model",
                status="completed",
                output_text="",
                output=(
                    SimpleNamespace(
                        type="function_call",
                        name="system_ping",
                        arguments="{}",
                        call_id="call-1",
                    ),
                ),
            )

        return SimpleNamespace(
            id="resp-2",
            model="test-model",
            status="completed",
            output_text="Jarvis is healthy.",
            output=(),
        )


async def main() -> None:
    api = FakeResponsesAPI()

    service = ResponsesService(
        responses_api=api,
        model="test-model",
    )

    first = await service.create_turn(
        input_items="Check health",
        tools=[
            {
                "type": "function",
                "name": "system_ping",
            }
        ],
    )

    assert first.requires_tool_output is True
    assert first.function_calls[0].name == "system_ping"

    second = await service.create_turn(
        input_items=[
            {
                "type": "function_call_output",
                "call_id": "call-1",
                "output": '{"success": true}',
            }
        ],
        previous_response_id=first.response_id,
    )

    assert second.output_text == "Jarvis is healthy."
    assert api.calls[1]["previous_response_id"] == "resp-1"

    print("Sprint 4.2 Pack C — Responses Tool Loop Integration")
    print("-" * 60)
    print("Function-call normalization: PASS")
    print("Continuation response id: PASS")
    print("Final text normalization: PASS")
    print("Sprint 4.2 Pack C live gate: PASS")


if __name__ == "__main__":
    asyncio.run(
        main()
    )
