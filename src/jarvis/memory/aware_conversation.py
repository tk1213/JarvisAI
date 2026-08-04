from __future__ import annotations

from jarvis.memory.capture import MemoryCaptureService
from jarvis.memory.commands import MemoryCommandService
from jarvis.memory.context import MemoryContextBuilder
from jarvis.services.ai_service import AIService
from jarvis.services.conversation_manager import ConversationManager
from jarvis.services.memory_service import (
    MemoryService as ConversationMemoryService,
)
from jarvis.services.tool_router import ToolRouter
from jarvis.smart_home.service import SmartHomeService


class MemoryAwareConversationManager(
    ConversationManager
):
    def __init__(
        self,
        *,
        ai: AIService,
        memory: ConversationMemoryService,
        router: ToolRouter,
        smart_home: SmartHomeService | None,
        memory_capture: MemoryCaptureService,
        memory_context: MemoryContextBuilder,
        memory_commands: MemoryCommandService,
    ) -> None:
        super().__init__(
            ai=ai,
            memory=memory,
            router=router,
            smart_home=smart_home,
        )

        self._memory_capture = memory_capture
        self._memory_context = memory_context
        self._memory_commands = memory_commands

    async def ask(
        self,
        text: str,
    ) -> str:
        command_reply = await self._memory_commands.handle(
            text
        )

        if command_reply is not None:
            await self._save_conversation(
                user_text=text,
                reply=command_reply,
                tool="memory",
            )
            return command_reply

        reply = await super().ask(
            text
        )

        if reply:
            await self._memory_capture.capture(
                text
            )

        return reply

    async def _ask_ai(
        self,
        text: str,
    ) -> str:
        memory_context = await self._memory_context.build(
            text
        )

        if not memory_context:
            return await super()._ask_ai(
                text
            )

        enriched_text = (
            f"{memory_context}\n\n"
            "[Current user message]\n"
            f"{text}"
        )

        return await super()._ask_ai(
            enriched_text
        )
