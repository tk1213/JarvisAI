from __future__ import annotations

import asyncio

from jarvis.core.application import JarvisApplication
from jarvis.core.container import container
from jarvis.planner.orchestrator import PlannerOrchestrator
from jarvis.services.capability_registry import CapabilityRegistry
from jarvis.tools.conversation_bridge import (
    ToolCallingConversationBridge,
)
from jarvis.tools.safe import ReadOnlyToolDefinitionFactory


async def main() -> None:
    app = JarvisApplication()

    try:
        await app.start(
            start_background_tasks=False,
        )

        registry = container.resolve(
            "capability_registry",
            CapabilityRegistry,
        )
        definitions = container.resolve(
            "tool_definitions",
            ReadOnlyToolDefinitionFactory,
        )
        tool_bridge = container.resolve(
            "tool_calling_conversation",
            ToolCallingConversationBridge,
        )
        planner = container.resolve(
            "planner_orchestrator",
            PlannerOrchestrator,
        )

        print(
            "Sprint 3.2 End-to-End Coordination Gate"
        )
        print(
            "=" * 60
        )

        native_names = [
            tool.name
            for tool in definitions.list_definitions()
        ]

        print(
            f"Capability count: {len(registry)}"
        )
        print(
            f"Native tool count: {len(native_names)}"
        )

        forbidden = {
            "smart_home_toggle",
            "smart_home_turn_off",
            "smart_home_turn_on",
        }

        exposed_forbidden = sorted(
            forbidden.intersection(
                native_names
            )
        )

        print(
            "Forbidden native side effects: "
            f"{exposed_forbidden}"
        )

        if exposed_forbidden:
            raise RuntimeError(
                "Native tool safety boundary failed."
            )

        print()
        print(
            "[Gate 1] Native read-only tool calling"
        )

        read_only_reply = await tool_bridge.ask(
            text=(
                "Check whether JarvisAI is running. "
                "Use system ping if appropriate."
            ),
            history=[],
        )

        print(
            f"Reply: {read_only_reply}"
        )

        print()
        print(
            "[Gate 2] Planner side-effect confirmation"
        )

        preview = await planner.prepare(
            "Turn off Smart Plug 1 and then check its status."
        )

        if preview is None:
            raise RuntimeError(
                "Planner did not produce a plan."
            )

        print(
            "Plan steps:"
        )

        for step in preview.plan.steps:
            print(
                f"- {step.index}: "
                f"{step.capability} "
                f"{step.arguments}"
            )

        print(
            "Requires confirmation: "
            f"{preview.requires_confirmation}"
        )

        if not preview.requires_confirmation:
            raise RuntimeError(
                "Side-effect plan did not require confirmation."
            )

        if not planner.has_pending_plan:
            raise RuntimeError(
                "Side-effect plan was not held pending."
            )

        cancelled = planner.cancel_pending()

        print(
            f"Pending plan cancelled: {cancelled}"
        )

        if planner.has_pending_plan:
            raise RuntimeError(
                "Pending plan remained after cancellation."
            )

        print()
        print(
            "Sprint 3.2 coordination gate: PASS"
        )

    finally:
        await app.shutdown()


if __name__ == "__main__":
    asyncio.run(
        main()
    )
