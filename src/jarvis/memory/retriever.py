from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import ClassVar

from jarvis.memory.models import Memory
from jarvis.memory.service import MemoryService


@dataclass(slots=True, frozen=True)
class RankedMemory:
    memory: Memory
    score: int


class MemoryRetriever:
    _KEY_ALIASES: ClassVar[
        dict[str, tuple[str, ...]]
    ] = {
        "user_name": (
            "name",
            "my name",
            "who am i",
            "ชื่อ",
            "ชื่อฉัน",
            "ชื่อผม",
            "ฉันชื่อ",
            "ผมชื่อ",
        ),
        "daughter_name": (
            "daughter",
            "daughter name",
            "my daughter",
            "ลูกสาว",
            "ชื่อลูกสาว",
        ),
        "son_name": (
            "son",
            "son name",
            "my son",
            "ลูกชาย",
            "ชื่อลูกชาย",
        ),
        "wife_name": (
            "wife",
            "wife name",
            "my wife",
            "ภรรยา",
            "ชื่อภรรยา",
        ),
        "husband_name": (
            "husband",
            "husband name",
            "my husband",
            "สามี",
            "ชื่อสามี",
        ),
        "favorite_drink": (
            "drink",
            "favorite drink",
            "what do i drink",
            "ชอบดื่ม",
            "เครื่องดื่ม",
            "ดื่มอะไร",
        ),
        "favorite_food": (
            "food",
            "favorite food",
            "what do i eat",
            "ชอบกิน",
            "อาหาร",
            "กินอะไร",
        ),
    }

    def __init__(
        self,
        memory: MemoryService,
        *,
        candidate_limit: int = 100,
    ) -> None:
        if candidate_limit < 1:
            raise ValueError(
                "candidate_limit must be at least 1."
            )

        self._memory = memory
        self._candidate_limit = candidate_limit

    async def retrieve(
        self,
        query: str,
        *,
        limit: int = 8,
    ) -> list[Memory]:
        if limit < 1:
            raise ValueError(
                "limit must be at least 1."
            )

        normalized_query = self._normalize(
            query
        )

        if not normalized_query:
            return []

        candidates = await self._memory.list_memories(
            limit=self._candidate_limit,
        )

        ranked: list[RankedMemory] = []

        for memory in candidates:
            score = self._score(
                normalized_query,
                memory,
            )

            if score <= 0:
                continue

            ranked.append(
                RankedMemory(
                    memory=memory,
                    score=score,
                )
            )

        ranked.sort(
            key=lambda item: (
                item.score,
                item.memory.importance.value,
                item.memory.updated_at,
            ),
            reverse=True,
        )

        return [
            item.memory
            for item in ranked[:limit]
        ]

    @classmethod
    def _score(
        cls,
        query: str,
        memory: Memory,
    ) -> int:
        score = 0

        key = cls._normalize(
            memory.key.replace(
                "_",
                " ",
            )
        )
        value = cls._normalize(
            memory.value
        )
        category = cls._normalize(
            memory.category.value.replace(
                "_",
                " ",
            )
        )

        if key and key in query:
            score += 12

        query_tokens = cls._tokens(
            query
        )
        key_tokens = cls._tokens(
            key
        )
        category_tokens = cls._tokens(
            category
        )

        score += (
            len(
                query_tokens
                & key_tokens
            )
            * 5
        )

        score += (
            len(
                query_tokens
                & category_tokens
            )
            * 2
        )

        if value and value in query:
            score += 6

        aliases = cls._KEY_ALIASES.get(
            memory.key,
            (),
        )

        for alias in aliases:
            normalized_alias = cls._normalize(
                alias
            )

            if (
                normalized_alias
                and normalized_alias in query
            ):
                score += 10

        return score

    @staticmethod
    def _normalize(
        text: str,
    ) -> str:
        normalized = unicodedata.normalize(
            "NFC",
            text,
        )

        normalized = normalized.casefold()

        normalized = re.sub(
            r"[^\w\s\u0E00-\u0E7F]",
            " ",
            normalized,
        )

        return " ".join(
            normalized.split()
        )

    @staticmethod
    def _tokens(
        text: str,
    ) -> set[str]:
        return {
            token
            for token in text.split()
            if len(token) >= 2
        }
