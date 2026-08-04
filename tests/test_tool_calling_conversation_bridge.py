from __future__ import annotations

from dataclasses import dataclass

import pytest

from jarvis.tools.conversation_bridge import (
    ToolCallingConversationBridge,
)


@dataclass
class FakeRunResult:
    text: str


class FakeRunner:
    def __init__(
        self,
        *,
        text: str = "tool answer",
        fail: bool = False,
    ) -> None:
        self.text = text
        self.fail = fail
        self.calls = []

    async def run(
        self,
        *,
        message: str,
        history=None,
    ):
        self.calls.append(
            (
                message,
                history,
            )
        )

        if self.fail:
            raise RuntimeError(
                "runner failed"
            )

        return FakeRunResult(
            text=self.text
        )


class FakeAI:
    def __init__(self) -> None:
        self.calls = []

    async def ask(
        self,
        *,
        text: str,
        history=None,
    ) -> str:
        self.calls.append(
            (
                text,
                history,
            )
        )

        return "fallback answer"


@pytest.mark.asyncio
async def test_bridge_uses_tool_runner() -> None:
    runner = FakeRunner(
        text="native tool answer"
    )
    fallback = FakeAI()

    bridge = ToolCallingConversationBridge(
        runner=runner,  # type: ignore[arg-type]
        fallback_ai=fallback,  # type: ignore[arg-type]
    )

    reply = await bridge.ask(
        text="check status",
        history=[
            {
                "role": "user",
                "content": "previous",
            }
        ],
    )

    assert reply == "native tool answer"
    assert len(runner.calls) == 1
    assert fallback.calls == []


@pytest.mark.asyncio
async def test_bridge_falls_back_when_runner_fails() -> None:
    runner = FakeRunner(
        fail=True
    )
    fallback = FakeAI()

    bridge = ToolCallingConversationBridge(
        runner=runner,  # type: ignore[arg-type]
        fallback_ai=fallback,  # type: ignore[arg-type]
    )

    reply = await bridge.ask(
        text="hello",
        history=[],
    )

    assert reply == "fallback answer"
    assert fallback.calls == [
        (
            "hello",
            [],
        )
    ]
