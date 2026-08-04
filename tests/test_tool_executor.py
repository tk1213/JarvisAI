from __future__ import annotations

from typing import Any

import pytest

from jarvis.tools.contracts import ToolCall
from jarvis.tools.executor import ToolExecutor


class StubRegistry:
    def __init__(
        self,
        allowed: set[str],
    ) -> None:
        self._allowed = allowed

    def is_allowed(
        self,
        capability: str,
    ) -> bool:
        return capability in self._allowed


class StubRouter:
    def __init__(
        self,
        *,
        fail: bool = False,
    ) -> None:
        self.fail = fail
        self.calls: list[str] = []

    async def execute_request(
        self,
        request,
    ) -> Any:
        self.calls.append(
            request.capability
        )

        if self.fail:
            raise RuntimeError(
                "boom"
            )

        return {
            "ok": True,
            "arguments": request.arguments,
        }


@pytest.mark.asyncio
async def test_allowed_tool_executes() -> None:
    registry = StubRegistry(
        {
            "system.ping",
        }
    )
    router = StubRouter()

    executor = ToolExecutor(
        registry=registry,  # type: ignore[arg-type]
        router=router,  # type: ignore[arg-type]
    )

    result = await executor.execute(
        ToolCall(
            name="system.ping",
            arguments={
                "x": 1,
            },
            call_id="call-1",
        )
    )

    assert result.success is True
    assert result.call_id == "call-1"
    assert result.output == {
        "ok": True,
        "arguments": {
            "x": 1,
        },
    }


@pytest.mark.asyncio
async def test_disallowed_tool_does_not_execute() -> None:
    registry = StubRegistry(
        {
            "system.ping",
        }
    )
    router = StubRouter()

    executor = ToolExecutor(
        registry=registry,  # type: ignore[arg-type]
        router=router,  # type: ignore[arg-type]
    )

    result = await executor.execute(
        ToolCall(
            name="dangerous.unknown",
        )
    )

    assert result.success is False
    assert result.error is not None
    assert result.error.code == "tool_not_allowed"
    assert router.calls == []


@pytest.mark.asyncio
async def test_execution_failure_is_structured() -> None:
    registry = StubRegistry(
        {
            "system.ping",
        }
    )
    router = StubRouter(
        fail=True
    )

    executor = ToolExecutor(
        registry=registry,  # type: ignore[arg-type]
        router=router,  # type: ignore[arg-type]
    )

    result = await executor.execute(
        ToolCall(
            name="system.ping",
        )
    )

    assert result.success is False
    assert result.error is not None
    assert result.error.code == "tool_execution_failed"
    assert result.error.message == "boom"
