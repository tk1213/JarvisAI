from __future__ import annotations

from pathlib import Path

RUNTIME_PATH = Path(
    "src/jarvis/agent/runtime.py"
)

BRIDGE_PATH = Path(
    "src/jarvis/agent/conversation_bridge.py"
)


def patch_runtime(text: str) -> str:
    anchor = (
        "    async def run(\n"
        "        self,\n"
        "        text: str,\n"
        "    ) -> AIAgentRunResult:\n"
    )

    insert = (
        "    @property\n"
        "    def has_pending_plan(self) -> bool:\n"
        "        return self._orchestrator.has_pending_plan\n"
        "\n"
    )

    if "def has_pending_plan(" not in text:
        if anchor not in text:
            raise SystemExit(
                "AIAgentRuntime run() anchor was not found."
            )

        text = text.replace(
            anchor,
            insert + anchor,
            1,
        )

    return text


def patch_bridge(text: str) -> str:
    old = (
        "    @property\n"
        "    def has_pending_plan(self) -> bool:\n"
        "        orchestrator = self._runtime._orchestrator\n"
        "        return orchestrator.has_pending_plan\n"
    )

    new = (
        "    @property\n"
        "    def has_pending_plan(self) -> bool:\n"
        "        return self._runtime.has_pending_plan\n"
    )

    if old in text:
        text = text.replace(
            old,
            new,
            1,
        )
    elif (
        "return self._runtime.has_pending_plan"
        not in text
    ):
        raise SystemExit(
            "AIAgentConversationBridge pending-plan block "
            "was not found."
        )

    return text


def main() -> None:
    runtime_text = RUNTIME_PATH.read_text(
        encoding="utf-8"
    )
    bridge_text = BRIDGE_PATH.read_text(
        encoding="utf-8"
    )

    RUNTIME_PATH.write_text(
        patch_runtime(runtime_text),
        encoding="utf-8",
    )

    BRIDGE_PATH.write_text(
        patch_bridge(bridge_text),
        encoding="utf-8",
    )

    print(
        "Sprint 4.1 Pack C safety hardening applied."
    )


if __name__ == "__main__":
    main()
