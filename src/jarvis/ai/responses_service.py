from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Protocol

from jarvis.ai.responses_contracts import (
    ResponsesFunctionCall,
    ResponsesTextResult,
    ResponsesTurnResult,
)


class ResponsesAPIProtocol(Protocol):
    async def create(
        self,
        **kwargs: Any,
    ) -> Any:
        ...


class ResponsesService:
    def __init__(
        self,
        *,
        responses_api: ResponsesAPIProtocol,
        model: str,
        max_output_tokens: int | None = None,
    ) -> None:
        normalized_model = model.strip()

        if not normalized_model:
            raise ValueError(
                "ResponsesService model cannot be empty."
            )

        if (
            max_output_tokens is not None
            and max_output_tokens < 1
        ):
            raise ValueError(
                "max_output_tokens must be at least 1."
            )

        self._responses_api = responses_api
        self._model = normalized_model
        self._max_output_tokens = max_output_tokens

    async def create_text(
        self,
        *,
        input_items: str | Sequence[dict[str, Any]],
        instructions: str | None = None,
    ) -> ResponsesTextResult:
        turn = await self.create_turn(
            input_items=input_items,
            instructions=instructions,
        )

        return ResponsesTextResult(
            response_id=turn.response_id,
            model=turn.model,
            status=turn.status,
            output_text=turn.output_text,
        )

    async def create_turn(
        self,
        *,
        input_items: str | Sequence[dict[str, Any]],
        instructions: str | None = None,
        tools: Sequence[dict[str, Any]] | None = None,
        previous_response_id: str | None = None,
        verbosity: str | None = None,
    ) -> ResponsesTurnResult:
        request: dict[str, Any] = {
            "model": self._model,
            "input": input_items,
        }

        if instructions is not None:
            request["instructions"] = instructions

        if verbosity is not None:
            if verbosity not in {
                "low",
                "medium",
                "high",
            }:
                raise ValueError(
                    "verbosity must be 'low', 'medium', or 'high'."
                )

            request["text"] = {
                "verbosity": verbosity,
            }    

        if tools:
            request["tools"] = list(
                tools
            )

        if previous_response_id is not None:
            normalized_response_id = previous_response_id.strip()

            if not normalized_response_id:
                raise ValueError(
                    "previous_response_id cannot be empty."
                )

            request["previous_response_id"] = (
                normalized_response_id
            )

        if self._max_output_tokens is not None:
            request["max_output_tokens"] = (
                self._max_output_tokens
            )

        response = await self._responses_api.create(
            **request
        )

        return self._normalize_response(
            response
        )

    def _normalize_response(
        self,
        response: Any,
    ) -> ResponsesTurnResult:
        output_text = str(
            getattr(
                response,
                "output_text",
                "",
            )
        ).strip()

        response_id = str(
            getattr(
                response,
                "id",
                "",
            )
        )

        status = str(
            getattr(
                response,
                "status",
                "unknown",
            )
        )

        model = str(
            getattr(
                response,
                "model",
                self._model,
            )
        )

        function_calls = tuple(
            self._normalize_function_call(
                item
            )
            for item in getattr(
                response,
                "output",
                (),
            )
            if getattr(
                item,
                "type",
                None,
            )
            == "function_call"
        )

        return ResponsesTurnResult(
            response_id=response_id,
            model=model,
            status=status,
            output_text=output_text,
            function_calls=function_calls,
        )

    @staticmethod
    def _normalize_function_call(
        item: Any,
    ) -> ResponsesFunctionCall:
        return ResponsesFunctionCall(
            name=str(
                getattr(
                    item,
                    "name",
                    "",
                )
            ),
            arguments=str(
                getattr(
                    item,
                    "arguments",
                    "{}",
                )
            ),
            call_id=getattr(
                item,
                "call_id",
                None,
            ),
        )
