from __future__ import annotations

from dataclasses import dataclass
from types import SimpleNamespace

import pytest

from jarvis.tools.contracts import ToolResult
from jarvis.tools.openai_runner import OpenAIToolCallingRunner


@dataclass
class FakeDefinitions:
    tools: list[dict]

    def to_openai_tools(
        self,
    ) -> list[dict]:
        return self.tools

    def resolve_capability_name(
        self,
        tool_name: str,
    ) -> str | None:
        mapping = {
            "system_ping": "system.ping",
        }

        return mapping.get(
            tool_name
        )


class FakeExecutor:
    def __init__(self) -> None:
        self.calls = []

    async def execute(
        self,
        call,
    ) -> ToolResult:
        self.calls.append(
            call
        )

        return ToolResult(
            name=call.name,
            success=True,
            output={
                "status": "ok",
            },
            call_id=call.call_id,
        )


class FakeResponses:
    def __init__(
        self,
        responses,
    ) -> None:
        self._responses = list(
            responses
        )
        self.calls = []

    async def create(
        self,
        **kwargs,
    ):
        self.calls.append(
            kwargs
        )

        return self._responses.pop(
            0
        )


class FakeAI:
    def __init__(
        self,
        responses,
    ) -> None:
        self.model = "test-model"
        self.client = SimpleNamespace(
            responses=FakeResponses(
                responses
            )
        )

    def _build_conversation(
        self,
        message,
        history=None,
    ):
        return [
            *(
                history
                or []
            ),
            {
                "role": "user",
                "content": message,
            },
        ]

    async def chat(
        self,
        message,
        history=None,
    ):
        del message, history

        return "fallback"


def function_call_response():
    return SimpleNamespace(
        id="resp-1",
        output=[
            SimpleNamespace(
                type="function_call",
                name="system_ping",
                arguments="{}",
                call_id="call-1",
            )
        ],
        output_text="",
    )


def final_response():
    return SimpleNamespace(
        id="resp-2",
        output=[],
        output_text="Jarvis is healthy.",
    )


@pytest.mark.asyncio
async def test_runner_executes_function_call_and_continues() -> None:
    ai = FakeAI(
        [
            function_call_response(),
            final_response(),
        ]
    )

    definitions = FakeDefinitions(
        [
            {
                "type": "function",
                "name": "system_ping",
                "description": "Ping",
                "parameters": {
                    "type": "object",
                    "properties": {},
                },
            }
        ]
    )

    executor = FakeExecutor()

    runner = OpenAIToolCallingRunner(
        ai=ai,  # type: ignore[arg-type]
        definitions=definitions,  # type: ignore[arg-type]
        executor=executor,  # type: ignore[arg-type]
    )

    result = await runner.run(
        "Is Jarvis healthy?"
    )

    assert result.text == "Jarvis is healthy."
    assert len(result.tool_results) == 1
    assert executor.calls[0].name == "system.ping"

    second_request = (
        ai.client.responses.calls[1]
    )

    assert (
        second_request["previous_response_id"]
        == "resp-1"
    )

    assert (
        second_request["input"][0]["type"]
        == "function_call_output"
    )

    assert (
        second_request["input"][0]["call_id"]
        == "call-1"
    )


@pytest.mark.asyncio
async def test_runner_returns_direct_text_without_tool_call() -> None:
    ai = FakeAI(
        [
            SimpleNamespace(
                id="resp-1",
                output=[],
                output_text="Hello.",
            )
        ]
    )

    runner = OpenAIToolCallingRunner(
        ai=ai,  # type: ignore[arg-type]
        definitions=FakeDefinitions(  # type: ignore[arg-type]
            [
                {
                    "type": "function",
                    "name": "system_ping",
                }
            ]
        ),
        executor=FakeExecutor(),  # type: ignore[arg-type]
    )

    result = await runner.run(
        "Hello"
    )

    assert result.text == "Hello."
    assert result.tool_results == ()


def test_invalid_arguments_are_rejected() -> None:
    runner = OpenAIToolCallingRunner(
        ai=FakeAI([]),  # type: ignore[arg-type]
        definitions=FakeDefinitions([]),  # type: ignore[arg-type]
        executor=FakeExecutor(),  # type: ignore[arg-type]
    )

    item = SimpleNamespace(
        name="system_ping",
        arguments="not-json",
        call_id="call-1",
    )

    with pytest.raises(
        ValueError,
        match="invalid tool arguments",
    ):
        runner._to_tool_call(
            item
        )


def test_unknown_tool_name_is_rejected() -> None:
    runner = OpenAIToolCallingRunner(
        ai=FakeAI([]),  # type: ignore[arg-type]
        definitions=FakeDefinitions([]),  # type: ignore[arg-type]
        executor=FakeExecutor(),  # type: ignore[arg-type]
    )

    item = SimpleNamespace(
        name="unknown_tool",
        arguments="{}",
        call_id="call-1",
    )

    with pytest.raises(
        ValueError,
        match="unknown tool name",
    ):
        runner._to_tool_call(
            item
        )
