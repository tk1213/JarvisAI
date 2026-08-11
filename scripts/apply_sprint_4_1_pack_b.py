from __future__ import annotations

from pathlib import Path

APPLICATION_PATH = Path(
    "src/jarvis/core/application.py"
)

CONVERSATION_PATH = Path(
    "src/jarvis/services/conversation_manager.py"
)


def patch_application(text: str) -> str:
    import_anchor = (
        "from jarvis.agent.bootstrap import "
        "register_ai_agent_runtime\n"
    )
    import_insert = (
        "from jarvis.agent.conversation_bridge import "
        "AIAgentConversationBridge\n"
    )

    if import_insert not in text:
        if import_anchor not in text:
            raise SystemExit(
                "Agent bootstrap import anchor not found."
            )

        text = text.replace(
            import_anchor,
            import_anchor + import_insert,
            1,
        )

    register_anchor = (
        "            register_ai_agent_runtime(\n"
        "                container,\n"
        "                overwrite=False,\n"
        "            )\n"
    )

    register_insert = (
        register_anchor
        + "\n"
        + "            ai_agent_runtime = container.get(\n"
        + '                "ai_agent_runtime"\n'
        + "            )\n"
        + "\n"
        + "            ai_agent_conversation = (\n"
        + "                AIAgentConversationBridge(\n"
        + "                    ai_agent_runtime\n"
        + "                )\n"
        + "            )\n"
        + "\n"
        + "            conversation_manager.set_ai_agent_bridge(\n"
        + "                ai_agent_conversation\n"
        + "            )\n"
        + "\n"
        + "            container.register(\n"
        + '                "ai_agent_conversation",\n'
        + "                ai_agent_conversation,\n"
        + "                overwrite=False,\n"
        + "            )\n"
    )

    if '"ai_agent_conversation"' not in text:
        if register_anchor not in text:
            raise SystemExit(
                "Agent runtime registration anchor not found."
            )

        text = text.replace(
            register_anchor,
            register_insert,
            1,
        )

    return text


def patch_conversation(text: str) -> str:
    import_anchor = (
        "from jarvis.core.events import Event\n"
    )
    import_insert = (
        "from jarvis.agent.conversation_bridge import "
        "AIAgentConversationBridge\n"
    )

    if import_insert not in text:
        if import_anchor not in text:
            raise SystemExit(
                "Conversation import anchor not found."
            )

        text = text.replace(
            import_anchor,
            import_anchor + import_insert,
            1,
        )

    field_anchor = (
        "        self._planner_bridge: "
        "PlannerConversationBridge | None = None\n"
    )
    field_insert = (
        field_anchor
        + "        self._ai_agent_bridge: "
        "AIAgentConversationBridge | None = None\n"
    )

    if "self._ai_agent_bridge:" not in text:
        if field_anchor not in text:
            raise SystemExit(
                "Conversation field anchor not found."
            )

        text = text.replace(
            field_anchor,
            field_insert,
            1,
        )

    setter_anchor = (
        "    def set_planner_bridge(\n"
    )
    setter_insert = (
        "    def set_ai_agent_bridge(\n"
        "        self,\n"
        "        bridge: AIAgentConversationBridge,\n"
        "    ) -> None:\n"
        "        self._ai_agent_bridge = bridge\n"
        "\n"
    )

    if "def set_ai_agent_bridge(" not in text:
        if setter_anchor not in text:
            raise SystemExit(
                "Conversation setter anchor not found."
            )

        text = text.replace(
            setter_anchor,
            setter_insert + setter_anchor,
            1,
        )

    pending_anchor = (
        "        if (\n"
        "            self._planner_bridge is not None\n"
        "            and self._planner_bridge.has_pending_plan\n"
        "        ):\n"
    )
    pending_insert = (
        "        if (\n"
        "            self._ai_agent_bridge is not None\n"
        "            and self._ai_agent_bridge.has_pending_plan\n"
        "        ):\n"
        "            agent_reply = (\n"
        "                await self._ai_agent_bridge.handle_pending(\n"
        "                    text\n"
        "                )\n"
        "            )\n"
        "\n"
        "            if agent_reply.handled:\n"
        "                await self._save_conversation(\n"
        "                    user_text=text,\n"
        "                    reply=agent_reply.reply,\n"
        '                    tool="ai_agent",\n'
        "                )\n"
        "                return agent_reply.reply\n"
        "\n"
    )

    if "await self._ai_agent_bridge.handle_pending(" not in text:
        if pending_anchor not in text:
            raise SystemExit(
                "Conversation pending anchor not found."
            )

        text = text.replace(
            pending_anchor,
            pending_insert + pending_anchor,
            1,
        )

    ai_anchor = (
        "    async def _handle_ai_route(\n"
        "        self,\n"
        "        text: str,\n"
        "    ) -> str:\n"
    )
    ai_insert = (
        ai_anchor
        + "        if self._ai_agent_bridge is not None:\n"
        + "            agent_reply = (\n"
        + "                await self._ai_agent_bridge.handle_ai_request(\n"
        + "                    text\n"
        + "                )\n"
        + "            )\n"
        + "\n"
        + "            if agent_reply.handled:\n"
        + "                return agent_reply.reply\n"
        + "\n"
    )

    if "await self._ai_agent_bridge.handle_ai_request(" not in text:
        if ai_anchor not in text:
            raise SystemExit(
                "Conversation AI route anchor not found."
            )

        text = text.replace(
            ai_anchor,
            ai_insert,
            1,
        )

    return text


def main() -> None:
    app_text = APPLICATION_PATH.read_text(
        encoding="utf-8"
    )
    conversation_text = CONVERSATION_PATH.read_text(
        encoding="utf-8"
    )

    APPLICATION_PATH.write_text(
        patch_application(app_text),
        encoding="utf-8",
    )
    CONVERSATION_PATH.write_text(
        patch_conversation(conversation_text),
        encoding="utf-8",
    )

    print(
        "Sprint 4.1 Pack B conversation integration applied."
    )


if __name__ == "__main__":
    main()
