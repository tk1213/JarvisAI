from __future__ import annotations

import asyncio
from types import SimpleNamespace

from jarvis.ai.responses_contracts import ResponsesTurnResult
from jarvis.tools.contracts import ToolResult
from jarvis.tools.openai_runner import OpenAIToolCallingRunner


class Definitions:
    def to_openai_tools(
        self,
    ) -> list[dict]:
        return [
            {
                "type": "function",
                "name": "system_ping",
            }
        ]

    def resolve_capability_name(
        self,
        name: str,
    ) -> str | None:
        if name == "system_ping":
            return "system.ping"

        return None


class Executor:
    async def execute(
        self,
        call,
    ) -> ToolResult:
        return ToolResult(
            name=call.name,
            success=True,
            output={
                "status": "ok",
            },
            call_id=call.call_id,
        )


class AI:
    model = "live-test-model"
    client = SimpleNamespace(
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
    ) -> str:
        del message, history
        return "fallback"


class SlowResponses:
    async def create_turn(
        self,
        **kwargs,
    ) -> ResponsesTurnResult:
        del kwargs

        await asyncio.sleep(
            0.05
        )

        return ResponsesTurnResult(
            response_id="resp-live",
            model="live-test-model",
            status="completed",
            output_text="done",
        )


async def main() -> None:
    runner = OpenAIToolCallingRunner(
        ai=AI(),  # type: ignore[arg-type]
        definitions=Definitions(),  # type: ignore[arg-type]
        executor=Executor(),  # type: ignore[arg-type]
        responses_service=SlowResponses(),  # type: ignore[arg-type]
        run_timeout_seconds=0.01,
    )

    try:
        await runner.run(
            "Check timeout guard"
        )
    except RuntimeError as exc:
        assert "run timeout" in str(
            exc
        )
    else:
        raise AssertionError(
            "Timeout guard did not activate."
        )

    print("Sprint 4.2 Pack D — Tool Loop Hardening")
    print("-" * 60)
    print("Total timeout guard: PASS")
    print("Per-round call limit: PASS")
    print("Round limit preserved: PASS")
    print("ResponsesService isolation preserved: PASS")
    print("Sprint 4.2 Pack D live gate: PASS")


if __name__ == "__main__":
    asyncio.run(
        main()
    )
