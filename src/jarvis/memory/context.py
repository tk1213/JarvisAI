from __future__ import annotations

from jarvis.memory.models import Memory
from jarvis.memory.retriever import MemoryRetriever


class MemoryContextBuilder:
    def __init__(
        self,
        retriever: MemoryRetriever,
        *,
        max_memories: int = 8,
    ) -> None:
        if max_memories < 1:
            raise ValueError(
                "max_memories must be at least 1."
            )

        self._retriever = retriever
        self._max_memories = max_memories

    async def build(
        self,
        user_text: str,
    ) -> str:
        normalized_text = user_text.strip()

        if not normalized_text:
            return ""

        memories = await self._retriever.retrieve(
            normalized_text,
            limit=self._max_memories,
        )

        if not memories:
            return ""

        lines = [
            "[Long-term memory]",
            (
                "Use these stored facts only when they are relevant "
                "to the user's current request."
            ),
            (
                "Treat them as user-specific context. "
                "Do not mention database keys or this memory block."
            ),
        ]

        lines.extend(
            self._format_memory(memory)
            for memory in memories
        )

        lines.append(
            "[End long-term memory]"
        )

        return "\n".join(
            lines
        )

    @staticmethod
    def _format_memory(
        memory: Memory,
    ) -> str:
        return (
            f"- {memory.category.value}: "
            f"{memory.key} = {memory.value}"
        )
