from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from jarvis.ai.openai_client import OpenAIClient
from jarvis.core.logger import log
from jarvis.core.prompt_manager import prompt_manager
from jarvis.tools.contracts import ToolCall, ToolResult
from jarvis.tools.definitions import ToolDefinitionFactory
from jarvis.tools.executor import ToolExecutor


@dataclass(slots=True, frozen=True)
class ToolCallingRunResult:
    text: str
    tool_results: tuple[ToolResult, ...]
    rounds: int


class OpenAIToolCallingRunner:
    def __init__(
        self,
        *,
        ai: OpenAIClient,
        definitions: ToolDefinitionFactory,
        executor: ToolExecutor,
        max_rounds: int = 4,
    ) -> None:
        if max_rounds < 1:
            raise ValueError(
                "max_rounds must be at least 1."
            )

        self._ai = ai
        self._definitions = definitions
        self._executor = executor
        self._max_rounds = max_rounds

    async def run(
        self,
        message: str,
        history: list[dict[str, str]] | None = None,
    ) -> ToolCallingRunResult:
        conversation = self._ai._build_conversation(
            message=message,
            history=history,
        )

        tools = self._definitions.to_openai_tools()

        if not tools:
            text = await self._ai.chat(
                message=message,
                history=history,
            )

            return ToolCallingRunResult(
                text=text,
                tool_results=(),
                rounds=0,
            )

        instructions = prompt_manager.load(
            "system"
        )

        response = await self._ai.client.responses.create(
            model=self._ai.model,
            instructions=instructions,
            input=conversation,
            tools=tools,
        )

        results: list[ToolResult] = []

        for round_number in range(
            1,
            self._max_rounds + 1,
        ):
            function_calls = self._function_calls(
                response
            )

            if not function_calls:
                return ToolCallingRunResult(
                    text=self._response_text(
                        response
                    ),
                    tool_results=tuple(
                        results
                    ),
                    rounds=round_number,
                )

            outputs: list[dict[str, Any]] = []

            for item in function_calls:
                call = self._to_tool_call(
                    item
                )

                result = await self._executor.execute(
                    call
                )

                results.append(
                    result
                )

                outputs.append(
                    {
                        "type": "function_call_output",
                        "call_id": call.call_id,
                        "output": self._serialize_tool_result(
                            result
                        ),
                    }
                )

            log.info(
                "Continuing OpenAI tool-calling response "
                "after {} tool call(s)",
                len(outputs),
            )

            response = await self._ai.client.responses.create(
                model=self._ai.model,
                instructions=instructions,
                previous_response_id=response.id,
                input=outputs,
                tools=tools,
            )

        raise RuntimeError(
            "OpenAI tool-calling exceeded maximum rounds."
        )

    @staticmethod
    def _function_calls(
        response: Any,
    ) -> list[Any]:
        output = getattr(
            response,
            "output",
            (),
        )

        return [
            item
            for item in output
            if getattr(
                item,
                "type",
                None,
            )
            == "function_call"
        ]

    def _to_tool_call(
        self,
        item: Any,
    ) -> ToolCall:
        tool_name = getattr(
            item,
            "name",
            "",
        )

        capability_name = (
            self._definitions.resolve_capability_name(
                tool_name
            )
        )

        if capability_name is None:
            raise ValueError(
                "OpenAI returned an unknown tool name: "
                f"{tool_name}"
            )

        call_id = getattr(
            item,
            "call_id",
            None,
        )

        raw_arguments = getattr(
            item,
            "arguments",
            "{}",
        )

        try:
            arguments = json.loads(
                raw_arguments
            )
        except (
            TypeError,
            json.JSONDecodeError,
        ) as exc:
            raise ValueError(
                "OpenAI returned invalid tool arguments."
            ) from exc

        if not isinstance(
            arguments,
            dict,
        ):
            raise TypeError(
                "OpenAI tool arguments must be a JSON object."
            )

        return ToolCall(
            name=capability_name,
            arguments=arguments,
            call_id=call_id,
        )

    @staticmethod
    def _serialize_tool_result(
        result: ToolResult,
    ) -> str:
        payload: dict[str, Any] = {
            "success": result.success,
            "output": result.output,
        }

        if result.error is not None:
            payload["error"] = {
                "code": result.error.code,
                "message": result.error.message,
            }

        return json.dumps(
            payload,
            ensure_ascii=False,
            default=str,
        )

    @staticmethod
    def _response_text(
        response: Any,
    ) -> str:
        text = str(
            getattr(
                response,
                "output_text",
                "",
            )
        ).strip()

        if text:
            return text

        return (
            "OpenAI completed the tool-calling turn "
            "without a text response."
        )
