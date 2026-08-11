from __future__ import annotations

from dataclasses import dataclass
from types import SimpleNamespace
from typing import Any

import pytest

from jarvis.ai.responses_service import ResponsesService


@dataclass
class FakeResponse:
    id: str = "resp_123"
    model: str = "gpt-5.5"
    status: str = "completed"
    output_text: str = "Jarvis is ready."
    output: tuple = ()


class FakeResponsesAPI:
    def __init__(
        self,
        response: FakeResponse | None = None,
    ) -> None:
        self.request: dict[str, Any] | None = None
        self.response = response or FakeResponse()

    async def create(
        self,
        **kwargs: Any,
    ) -> FakeResponse:
        self.request = dict(
            kwargs
        )
        return self.response


@pytest.mark.asyncio
async def test_responses_service_returns_metadata() -> None:
    api = FakeResponsesAPI()

    result = await ResponsesService(
        responses_api=api,
        model="gpt-5.5",
        max_output_tokens=512,
    ).create_text(
        input_items="Ping",
        instructions="Be concise.",
    )

    assert result.response_id == "resp_123"
    assert result.status == "completed"
    assert result.completed is True
    assert result.output_text == "Jarvis is ready."

    assert api.request == {
        "model": "gpt-5.5",
        "input": "Ping",
        "instructions": "Be concise.",
        "max_output_tokens": 512,
    }


@pytest.mark.asyncio
async def test_create_turn_normalizes_function_calls() -> None:
    api = FakeResponsesAPI(
        FakeResponse(
            output_text="",
            output=(
                SimpleNamespace(
                    type="function_call",
                    name="system_ping",
                    arguments="{}",
                    call_id="call_123",
                ),
            ),
        )
    )

    result = await ResponsesService(
        responses_api=api,
        model="gpt-5.5",
    ).create_turn(
        input_items="Check health",
        tools=[
            {
                "type": "function",
                "name": "system_ping",
            }
        ],
    )

    assert result.requires_tool_output is True
    assert result.function_calls[0].name == "system_ping"
    assert result.function_calls[0].call_id == "call_123"


@pytest.mark.asyncio
async def test_create_turn_supports_continuation() -> None:
    api = FakeResponsesAPI()

    await ResponsesService(
        responses_api=api,
        model="gpt-5.5",
    ).create_turn(
        input_items=[
            {
                "type": "function_call_output",
                "call_id": "call_123",
                "output": '{"success":true}',
            }
        ],
        previous_response_id="resp_previous",
    )

    assert api.request is not None
    assert (
        api.request["previous_response_id"]
        == "resp_previous"
    )


def test_responses_service_rejects_invalid_limits() -> None:
    with pytest.raises(
        ValueError,
        match="at least 1",
    ):
        ResponsesService(
            responses_api=FakeResponsesAPI(),
            model="gpt-5.5",
            max_output_tokens=0,
        )



@pytest.mark.asyncio
async def test_responses_service_normalizes_function_calls() -> None:
    from types import SimpleNamespace

    class ToolResponse:
        id = "resp_tool"
        model = "gpt-5.5"
        status = "completed"
        output_text = ""
        output = (
            SimpleNamespace(
                type="function_call",
                name="system_ping",
                arguments="{}",
                call_id="call_123",
            ),
        )

    api = FakeResponsesAPI()
    api.create = lambda **kwargs: None  # type: ignore[method-assign]

    async def create(**kwargs):
        api.request = dict(kwargs)
        return ToolResponse()

    api.create = create  # type: ignore[method-assign]

    result = await ResponsesService(
        responses_api=api,
        model="gpt-5.5",
    ).create_turn(
        input_items="Ping",
        tools=[
            {
                "type": "function",
                "name": "system_ping",
            }
        ],
    )

    assert result.requires_tool_output is True
    assert result.function_calls[0].name == "system_ping"
    assert result.function_calls[0].call_id == "call_123"


@pytest.mark.asyncio
async def test_responses_service_supports_previous_response_id() -> None:
    api = FakeResponsesAPI()

    await ResponsesService(
        responses_api=api,
        model="gpt-5.5",
    ).create_turn(
        input_items=[
            {
                "type": "function_call_output",
                "call_id": "call_123",
                "output": '{"success": true}',
            }
        ],
        previous_response_id="resp_previous",
    )

    assert api.request is not None
    assert api.request["previous_response_id"] == "resp_previous"
