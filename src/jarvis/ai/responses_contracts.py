from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class ResponsesFunctionCall:
    name: str
    arguments: str
    call_id: str | None = None

    def __post_init__(self) -> None:
        normalized_name = self.name.strip()

        if not normalized_name:
            raise ValueError(
                "ResponsesFunctionCall name cannot be empty."
            )

        object.__setattr__(
            self,
            "name",
            normalized_name,
        )


@dataclass(slots=True, frozen=True)
class ResponsesTurnResult:
    response_id: str
    model: str
    status: str
    output_text: str
    function_calls: tuple[ResponsesFunctionCall, ...] = ()

    @property
    def completed(self) -> bool:
        return self.status == "completed"

    @property
    def requires_tool_output(self) -> bool:
        return bool(
            self.function_calls
        )


@dataclass(slots=True, frozen=True)
class ResponsesTextResult:
    response_id: str
    model: str
    status: str
    output_text: str

    @property
    def completed(self) -> bool:
        return self.status == "completed"
