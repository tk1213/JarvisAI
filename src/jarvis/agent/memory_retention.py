from __future__ import annotations

from dataclasses import dataclass

from jarvis.agent.memory_repository import AIAgentMemoryRepository


@dataclass(slots=True, frozen=True)
class AIAgentMemoryRetentionResult:
    before: int
    deleted: int
    after: int


class AIAgentMemoryRetentionPolicy:
    def __init__(
        self,
        repository: AIAgentMemoryRepository,
        *,
        max_records: int = 500,
    ) -> None:
        if max_records < 1:
            raise ValueError(
                "max_records must be at least 1."
            )

        self._repository = repository
        self._max_records = max_records

    @property
    def max_records(self) -> int:
        return self._max_records

    async def enforce(
        self,
    ) -> AIAgentMemoryRetentionResult:
        before = await self._repository.count()

        if before <= self._max_records:
            return AIAgentMemoryRetentionResult(
                before=before,
                deleted=0,
                after=before,
            )

        deleted = await self._repository.delete_oldest(
            keep=self._max_records
        )

        after = max(
            0,
            before - deleted,
        )

        return AIAgentMemoryRetentionResult(
            before=before,
            deleted=deleted,
            after=after,
        )
