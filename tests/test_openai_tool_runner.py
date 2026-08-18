from __future__ import annotations

import asyncio
from dataclasses import dataclass
from types import SimpleNamespace

import pytest

from jarvis.ai.responses_contracts import (
    ResponsesFunctionCall,
    ResponsesTurnResult,
)
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


class FakeResponsesService:
    def __init__(
        self,
        responses,
    ) -> None:
        self._responses = list(
            responses
        )
        self.calls = []

    async def create_turn(
        self,
        **kwargs,
    ) -> ResponsesTurnResult:
        self.calls.append(
            kwargs
        )

        return self._responses.pop(
            0
        )


class FakeAI:
    def __init__(self) -> None:
        self.model = "test-model"
        self.client = SimpleNamespace(
            responses=SimpleNamespace()
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


def function_call_response() -> ResponsesTurnResult:
    return ResponsesTurnResult(
        response_id="resp-1",
        model="test-model",
        status="completed",
        output_text="",
        function_calls=(
            ResponsesFunctionCall(
                name="system_ping",
                arguments="{}",
                call_id="call-1",
            ),
        ),
    )


def final_response() -> ResponsesTurnResult:
    return ResponsesTurnResult(
        response_id="resp-2",
        model="test-model",
        status="completed",
        output_text="Jarvis is healthy.",
    )


@pytest.mark.asyncio
async def test_runner_executes_function_call_and_continues() -> None:
    responses = FakeResponsesService(
        [
            function_call_response(),
            final_response(),
        ]
    )

    executor = FakeExecutor()

    runner = OpenAIToolCallingRunner(
        ai=FakeAI(),  # type: ignore[arg-type]
        definitions=FakeDefinitions(  # type: ignore[arg-type]
            [
                {
                    "type": "function",
                    "name": "system_ping",
                }
            ]
        ),
        executor=executor,  # type: ignore[arg-type]
        responses_service=responses,  # type: ignore[arg-type]
    )

    result = await runner.run(
        "Is Jarvis healthy?"
    )

    assert result.text == "Jarvis is healthy."
    assert len(result.tool_results) == 1
    assert executor.calls[0].name == "system.ping"

    second_request = responses.calls[1]

    assert second_request["previous_response_id"] == "resp-1"
    assert (
        second_request["input_items"][0]["type"]
        == "function_call_output"
    )
    assert (
        second_request["input_items"][0]["call_id"]
        == "call-1"
    )


@pytest.mark.asyncio
async def test_runner_returns_direct_text_without_tool_call() -> None:
    responses = FakeResponsesService(
        [
            final_response(),
        ]
    )

    runner = OpenAIToolCallingRunner(
        ai=FakeAI(),  # type: ignore[arg-type]
        definitions=FakeDefinitions(  # type: ignore[arg-type]
            [
                {
                    "type": "function",
                    "name": "system_ping",
                }
            ]
        ),
        executor=FakeExecutor(),  # type: ignore[arg-type]
        responses_service=responses,  # type: ignore[arg-type]
    )

    result = await runner.run(
        "Hello"
    )

    assert result.text == "Jarvis is healthy."
    assert result.tool_results == ()


def test_invalid_arguments_are_rejected() -> None:
    runner = OpenAIToolCallingRunner(
        ai=FakeAI(),  # type: ignore[arg-type]
        definitions=FakeDefinitions([]),  # type: ignore[arg-type]
        executor=FakeExecutor(),  # type: ignore[arg-type]
        responses_service=FakeResponsesService([]),  # type: ignore[arg-type]
    )

    item = ResponsesFunctionCall(
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
        ai=FakeAI(),  # type: ignore[arg-type]
        definitions=FakeDefinitions([]),  # type: ignore[arg-type]
        executor=FakeExecutor(),  # type: ignore[arg-type]
        responses_service=FakeResponsesService([]),  # type: ignore[arg-type]
    )

    item = ResponsesFunctionCall(
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



def test_runner_rejects_invalid_timeout() -> None:
    with pytest.raises(
        ValueError,
        match="run_timeout_seconds",
    ):
        OpenAIToolCallingRunner(
            ai=FakeAI(),  # type: ignore[arg-type]
            definitions=FakeDefinitions([]),  # type: ignore[arg-type]
            executor=FakeExecutor(),  # type: ignore[arg-type]
            responses_service=FakeResponsesService([]),  # type: ignore[arg-type]
            run_timeout_seconds=0,
        )


def test_runner_rejects_invalid_tool_call_limit() -> None:
    with pytest.raises(
        ValueError,
        match="max_tool_calls_per_round",
    ):
        OpenAIToolCallingRunner(
            ai=FakeAI(),  # type: ignore[arg-type]
            definitions=FakeDefinitions([]),  # type: ignore[arg-type]
            executor=FakeExecutor(),  # type: ignore[arg-type]
            responses_service=FakeResponsesService([]),  # type: ignore[arg-type]
            max_tool_calls_per_round=0,
        )


@pytest.mark.asyncio
async def test_runner_blocks_excessive_calls_in_one_round() -> None:
    calls = tuple(
        ResponsesFunctionCall(
            name="system_ping",
            arguments="{}",
            call_id=f"call-{index}",
        )
        for index in range(3)
    )

    responses = FakeResponsesService(
        [
            ResponsesTurnResult(
                response_id="resp-1",
                model="test-model",
                status="completed",
                output_text="",
                function_calls=calls,
            )
        ]
    )

    runner = OpenAIToolCallingRunner(
        ai=FakeAI(),  # type: ignore[arg-type]
        definitions=FakeDefinitions(  # type: ignore[arg-type]
            [
                {
                    "type": "function",
                    "name": "system_ping",
                }
            ]
        ),
        executor=FakeExecutor(),  # type: ignore[arg-type]
        responses_service=responses,  # type: ignore[arg-type]
        max_tool_calls_per_round=2,
    )

    with pytest.raises(
        RuntimeError,
        match="maximum tool calls",
    ):
        await runner.run(
            "Run too many tools"
        )


@pytest.mark.asyncio
async def test_runner_enforces_total_timeout() -> None:
    class SlowResponsesService:
        async def create_turn(
            self,
            **kwargs,
        ) -> ResponsesTurnResult:
            del kwargs

            await asyncio.sleep(
                0.05
            )

            return final_response()

    runner = OpenAIToolCallingRunner(
        ai=FakeAI(),  # type: ignore[arg-type]
        definitions=FakeDefinitions(  # type: ignore[arg-type]
            [
                {
                    "type": "function",
                    "name": "system_ping",
                }
            ]
        ),
        executor=FakeExecutor(),  # type: ignore[arg-type]
        responses_service=SlowResponsesService(),  # type: ignore[arg-type]
        run_timeout_seconds=0.01,
    )

    with pytest.raises(
        RuntimeError,
        match="run timeout",
    ):
        await runner.run(
            "Check health"
        )

@pytest.mark.asyncio
async def test_runner_preserves_external_cancellation() -> None:
    entered = asyncio.Event()

    class BlockingResponsesService:
        async def create_turn(
            self,
            **kwargs,
        ) -> ResponsesTurnResult:
            del kwargs

            entered.set()
            await asyncio.Future()

            return final_response()

    runner = OpenAIToolCallingRunner(
        ai=FakeAI(),  # type: ignore[arg-type]
        definitions=FakeDefinitions(  # type: ignore[arg-type]
            [
                {
                    "type": "function",
                    "name": "system_ping",
                }
            ]
        ),
        executor=FakeExecutor(),  # type: ignore[arg-type]
        responses_service=BlockingResponsesService(),  # type: ignore[arg-type]
        run_timeout_seconds=10.0,
    )

    task = asyncio.create_task(
        runner.run(
            "Check health"
        )
    )

    await entered.wait()

    task.cancel()

    with pytest.raises(
        asyncio.CancelledError,
    ):
        await task