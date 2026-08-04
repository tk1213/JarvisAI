from __future__ import annotations

import asyncio

from jarvis.core.application import JarvisApplication
from jarvis.core.container import container
from jarvis.tools.conversation_bridge import (
    ToolCallingConversationBridge,
)
from jarvis.tools.safe import (
    ReadOnlyToolDefinitionFactory,
    ReadOnlyToolExecutor,
)


async def main() -> None:
    app = JarvisApplication()

    try:
        await app.start(
            start_background_tasks=False,
        )

        bridge = container.resolve(
            "tool_calling_conversation",
            ToolCallingConversationBridge,
        )

        definitions = container.resolve(
            "tool_definitions",
            ReadOnlyToolDefinitionFactory,
        )

        container.resolve(
            "tool_executor",
            ReadOnlyToolExecutor,
        )

        print(
            "Native tool calling runtime"
        )
        print(
            "-" * 60
        )

        print(
            "Available native tools:"
        )

        tools = definitions.list_definitions()

        for tool in tools:
            print(
                f"- {tool.name}"
            )

        side_effect_exposed = any(
            (
                "turn_on" in tool.name
                or "turn_off" in tool.name
            )
            for tool in tools
        )

        print()
        print(
            "Side-effect tools exposed: "
            f"{side_effect_exposed}"
        )

        reply = await bridge.ask(
            text=(
                "Check whether JarvisAI is running. "
                "Use system ping if appropriate."
            ),
            history=[],
        )

        print()
        print(
            f"Reply: {reply}"
        )

    finally:
        await app.shutdown()


if __name__ == "__main__":
    asyncio.run(
        main()
    )
