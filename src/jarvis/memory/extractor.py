from __future__ import annotations

import unicodedata
from collections.abc import Iterable
from typing import ClassVar

from jarvis.memory.extracted_memory import ExtractedMemory
from jarvis.memory.rules import MEMORY_RULES, MemoryRule


class MemoryExtractor:
    _REJECTED_VALUES: ClassVar[frozenset[str]] = frozenset(
        {
            # Thai question / unknown placeholders
            "อะไร",
            "ใคร",
            "ที่ไหน",
            "เมื่อไหร่",
            "อย่างไร",
            "เท่าไหร่",
            "กี่",
            # English question / unknown placeholders
            "what",
            "who",
            "where",
            "when",
            "how",
            "unknown",
            "none",
            "null",
        }
    )

    def __init__(
        self,
        rules: Iterable[MemoryRule] = MEMORY_RULES,
    ) -> None:
        self._rules = tuple(rules)

    def extract(
        self,
        text: str,
    ) -> list[ExtractedMemory]:
        normalized_text = self._normalize_text(
            text
        )

        if not normalized_text:
            return []

        extracted: list[ExtractedMemory] = []
        seen: set[tuple[str, str]] = set()

        for rule in self._rules:
            for match in rule.pattern.finditer(
                normalized_text
            ):
                value = self._clean_value(
                    match.group("value")
                )

                if not self._is_valid_value(
                    value
                ):
                    continue

                identity = (
                    rule.key,
                    value.casefold(),
                )

                if identity in seen:
                    continue

                seen.add(identity)

                extracted.append(
                    ExtractedMemory(
                        category=rule.category,
                        key=rule.key,
                        value=value,
                        importance=rule.importance,
                    )
                )

        return extracted

    @classmethod
    def _is_valid_value(
        cls,
        value: str,
    ) -> bool:
        normalized = cls._normalize_text(
            value
        ).casefold()

        if not normalized:
            return False

        return normalized not in cls._REJECTED_VALUES

    @staticmethod
    def _normalize_text(
        text: str,
    ) -> str:
        normalized = unicodedata.normalize(
            "NFC",
            text,
        )

        normalized = normalized.replace(
            "\u0e4d\u0e32",
            "\u0e33",
        )

        return " ".join(
            normalized.strip().split()
        )

    @staticmethod
    def _clean_value(
        value: str,
    ) -> str:
        return value.strip(
            " \t\r\n,.;!?，。"
        )
