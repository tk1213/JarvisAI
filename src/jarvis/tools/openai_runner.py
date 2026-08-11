from __future__ import annotations

import asyncio
import json
import time
from dataclasses import dataclass
from typing import Any

from jarvis.ai.openai_client import OpenAIClient
from jarvis.ai.responses_contracts import (
    ResponsesFunctionCall,
    ResponsesTurnResult,
)
from jarvis.ai.responses_service import ResponsesService
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
        responses_service: ResponsesService | None = None,
        run_timeout_seconds: float = 30.0,
        max_tool_calls_per_round: int = 8,
    ) -> None:
        if max_rounds < 1:
            raise ValueError(
                "max_rounds must be at least 1."
            )

        if run_timeout_seconds <= 0:
            raise ValueError(
                "run_timeout_seconds must be greater than 0."
            )

        if max_tool_calls_per_round < 1:
            raise ValueError(
                "max_tool_calls_per_round must be at least 1."
            )

        self._ai = ai
        self._definitions = definitions
        self._executor = executor
        self._max_rounds = max_rounds
        self._run_timeout_seconds = run_timeout_seconds
        self._max_tool_calls_per_round = max_tool_calls_per_round

        self._responses = (
            responses_service
            if responses_service is not None
            else ResponsesService(
                responses_api=ai.client.responses,
                model=ai.model,
            )
        )

    async def run(
        self,
        message: str,
        history: list[dict[str, str]] | None = None,
        *,
        voice_mode: bool = False,
    ) -> ToolCallingRunResult:
        started_at = time.monotonic()

        try:
            async with asyncio.timeout(
                self._run_timeout_seconds
            ):
                result = await self._run(
                    message=message,
                    history=history,
                    voice_mode=voice_mode,
                )
        except TimeoutError as exc:
            elapsed = time.monotonic() - started_at

            log.warning(
                "OpenAI tool-calling timed out after {:.3f}s",
                elapsed,
            )

            raise RuntimeError(
                "OpenAI tool-calling exceeded the run timeout."
            ) from exc

        elapsed = time.monotonic() - started_at

        log.info(
            "OpenAI tool-calling completed in {:.3f}s "
            "after {} round(s) with {} tool result(s)",
            elapsed,
            result.rounds,
            len(result.tool_results),
        )

        return result

    async def _run(
        self,
        *,
        message: str,
        history: list[dict[str, str]] | None,
        voice_mode: bool,
    ) -> ToolCallingRunResult:
        conversation = self._ai._build_conversation(
            message=message,
            history=history,
        )

        tools = self._definitions.to_openai_tools()

        if not tools:
            if voice_mode:
                text = await self._ai.chat(
                    message=message,
                    history=history,
                    voice_mode=True,
                )
            else:
                text = await self._ai.chat(
                    message=message,
                    history=history,
                )

            return ToolCallingRunResult(
                text=text,
                tool_results=(),
                rounds=0,
            )

        instructions = self._build_instructions(
            voice_mode=voice_mode,
        )

        response = await self._responses.create_turn(
            input_items=conversation,
            instructions=instructions,
            tools=tools,
            verbosity=(
                "low"
                if voice_mode
                else None
            ),
        )

        results: list[ToolResult] = []

        for round_number in range(
            1,
            self._max_rounds + 1,
        ):
            function_calls = response.function_calls

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

            self._validate_function_call_count(
                function_calls
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

            response = await self._responses.create_turn(
                input_items=outputs,
                instructions=instructions,
                previous_response_id=response.response_id,
                tools=tools,
            )

        raise RuntimeError(
            "OpenAI tool-calling exceeded maximum rounds."
        )

   
    def _build_instructions(
        self,
        *,
        voice_mode: bool,
    ) -> str:
        instructions = prompt_manager.load(
            "system"
        )

        if not voice_mode:
            return instructions

        voice_instructions = (
            "\n\n"
            "Voice response mode:\n"
            "- This response will be spoken aloud.\n"
            "- Default to ONE very short sentence.\n"
            "- Give the answer immediately.\n"
            "- For recommendations, give only ONE best recommendation.\n"
            "- Do not explain why unless the user asks why.\n"
            "- Do not add benefits, reasons, examples, or alternatives "
            "unless requested.\n"
            "- Do not repeat or paraphrase the user's message.\n"
            "- Avoid filler and conversational padding.\n"
            "- Do not use Markdown, headings, bullet lists, tables, or emojis.\n"
            "- Use additional sentences only when necessary for correctness "
            "or safety.\n"
            "- If the user explicitly asks for details, steps, options, "
            "or an explanation, provide the necessary detail.\n"
            "- Never omit important safety information for brevity."
        )

        return instructions + voice_instructions

    def _validate_function_call_count(
        self,
        function_calls: tuple[ResponsesFunctionCall, ...],
    ) -> None:
        if (
            len(function_calls)
            > self._max_tool_calls_per_round
        ):
            raise RuntimeError(
                "OpenAI tool-calling exceeded the maximum "
                "tool calls allowed in one round."
            )

    def _to_tool_call(
        self,
        item: ResponsesFunctionCall,
    ) -> ToolCall:
        capability_name = (
            self._definitions.resolve_capability_name(
                item.name
            )
        )

        if capability_name is None:
            raise ValueError(
                "OpenAI returned an unknown tool name: "
                f"{item.name}"
            )

        try:
            arguments = json.loads(
                item.arguments
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
            call_id=item.call_id,
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
        response: ResponsesTurnResult,
    ) -> str:
        if response.output_text:
            return response.output_text

        return (
            "OpenAI completed the tool-calling turn "
            "without a text response."
        )