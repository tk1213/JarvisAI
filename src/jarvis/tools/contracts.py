from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class ToolCallStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(slots=True, frozen=True)
class ToolCall:
    name: str
    arguments: dict[str, Any] = field(
        default_factory=dict
    )
    call_id: str | None = None

    def __post_init__(self) -> None:
        normalized_name = self.name.strip()

        if not normalized_name:
            raise ValueError(
                "ToolCall name cannot be empty."
            )

        object.__setattr__(
            self,
            "name",
            normalized_name,
        )


@dataclass(slots=True, frozen=True)
class ToolError:
    code: str
    message: str

    def __post_init__(self) -> None:
        code = self.code.strip()
        message = self.message.strip()

        if not code:
            raise ValueError(
                "ToolError code cannot be empty."
            )

        if not message:
            raise ValueError(
                "ToolError message cannot be empty."
            )

        object.__setattr__(
            self,
            "code",
            code,
        )
        object.__setattr__(
            self,
            "message",
            message,
        )


@dataclass(slots=True, frozen=True)
class ToolResult:
    name: str
    success: bool
    output: Any = None
    error: ToolError | None = None
    call_id: str | None = None

    def __post_init__(self) -> None:
        normalized_name = self.name.strip()

        if not normalized_name:
            raise ValueError(
                "ToolResult name cannot be empty."
            )

        if self.success and self.error is not None:
            raise ValueError(
                "Successful ToolResult cannot contain an error."
            )

        if not self.success and self.error is None:
            raise ValueError(
                "Failed ToolResult must contain an error."
            )

        object.__setattr__(
            self,
            "name",
            normalized_name,
        )
