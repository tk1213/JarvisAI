import pytest

from jarvis.tools.contracts import (
    ToolCall,
    ToolError,
    ToolResult,
)


def test_tool_call_normalizes_name() -> None:
    call = ToolCall(
        name=" system.ping ",
        arguments={},
    )

    assert call.name == "system.ping"


def test_tool_call_rejects_empty_name() -> None:
    with pytest.raises(
        ValueError,
        match="name",
    ):
        ToolCall(
            name=" ",
        )


def test_success_result_rejects_error() -> None:
    with pytest.raises(
        ValueError,
        match="Successful",
    ):
        ToolResult(
            name="system.ping",
            success=True,
            error=ToolError(
                code="x",
                message="bad",
            ),
        )


def test_failed_result_requires_error() -> None:
    with pytest.raises(
        ValueError,
        match="must contain",
    ):
        ToolResult(
            name="system.ping",
            success=False,
        )
