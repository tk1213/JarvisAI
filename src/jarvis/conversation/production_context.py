from __future__ import annotations

from dataclasses import dataclass

from jarvis.conversation.context_assembly import (
    ConversationContextAssembler,
    ConversationContextAssembly,
    ConversationContextPriority,
    ConversationContextSection,
)
from jarvis.memory.coordination import ConversationAgentMemoryCoordinator


@dataclass(slots=True, frozen=True)
class ConversationProductionContext:
    text: str
    assembly: ConversationContextAssembly


class ConversationProductionContextBuilder:
    def __init__(
        self,
        *,
        memory_coordinator: ConversationAgentMemoryCoordinator,
        assembler: ConversationContextAssembler | None = None,
        system_text: str = "",
    ) -> None:
        self._memory_coordinator = memory_coordinator
        self._assembler = (
            assembler
            if assembler is not None
            else ConversationContextAssembler()
        )
        self._system_text = system_text

    async def build(
        self,
        *,
        user_text: str,
        history_text: str = "",
    ) -> ConversationProductionContext:
        coordinated = await self._memory_coordinator.build(
            user_text
        )

        sections: list[ConversationContextSection] = []

        if self._system_text:
            sections.append(
                ConversationContextSection(
                    name="SYSTEM",
                    text=self._system_text,
                    priority=ConversationContextPriority.SYSTEM,
                    required=True,
                )
            )

        if coordinated.text:
            sections.append(
                ConversationContextSection(
                    name="MEMORY CONTEXT",
                    text=coordinated.text,
                    priority=ConversationContextPriority.CONVERSATION_MEMORY,
                )
            )

        if history_text:
            sections.append(
                ConversationContextSection(
                    name="HISTORY",
                    text=history_text,
                    priority=ConversationContextPriority.HISTORY,
                )
            )

        sections.append(
            ConversationContextSection(
                name="CURRENT USER",
                text=user_text,
                priority=ConversationContextPriority.CURRENT_USER,
                required=True,
            )
        )

        assembly = self._assembler.assemble(
            tuple(
                sections
            )
        )

        return ConversationProductionContext(
            text=assembly.text,
            assembly=assembly,
        )
