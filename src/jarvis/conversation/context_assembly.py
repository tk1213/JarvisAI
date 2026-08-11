from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum


class ConversationContextPriority(IntEnum):
    SYSTEM = 10
    CONVERSATION_MEMORY = 20
    AGENT_MEMORY = 30
    HISTORY = 40
    CURRENT_USER = 50


@dataclass(slots=True, frozen=True)
class ConversationContextSection:
    name: str
    text: str
    priority: ConversationContextPriority
    required: bool = False


@dataclass(slots=True, frozen=True)
class ConversationContextDiagnostics:
    budget_chars: int
    used_chars: int
    included_sections: tuple[str, ...]
    dropped_sections: tuple[str, ...]

    @property
    def remaining_chars(self) -> int:
        return max(
            0,
            self.budget_chars - self.used_chars,
        )


@dataclass(slots=True, frozen=True)
class ConversationContextAssembly:
    text: str
    diagnostics: ConversationContextDiagnostics


class ConversationContextAssembler:
    """Build bounded production context with deterministic precedence."""

    def __init__(
        self,
        *,
        max_chars: int = 12000,
    ) -> None:
        if max_chars < 512:
            raise ValueError(
                "max_chars must be at least 512."
            )

        self._max_chars = max_chars

    @property
    def max_chars(self) -> int:
        return self._max_chars

    def assemble(
        self,
        sections: tuple[ConversationContextSection, ...],
    ) -> ConversationContextAssembly:
        ordered = tuple(
            sorted(
                (
                    section
                    for section in sections
                    if section.text.strip()
                ),
                key=lambda section: int(
                    section.priority
                ),
            )
        )

        included: list[ConversationContextSection] = []
        dropped: list[str] = []

        for section in ordered:
            candidate = self._render(
                (
                    *included,
                    section,
                )
            )

            if len(candidate) <= self._max_chars:
                included.append(
                    section
                )
                continue

            if section.required:
                raise ValueError(
                    f"Required context section '{section.name}' "
                    "exceeds the context budget."
                )

            dropped.append(
                section.name
            )

        text = self._render(
            tuple(
                included
            )
        )

        return ConversationContextAssembly(
            text=text,
            diagnostics=ConversationContextDiagnostics(
                budget_chars=self._max_chars,
                used_chars=len(text),
                included_sections=tuple(
                    section.name
                    for section in included
                ),
                dropped_sections=tuple(
                    dropped
                ),
            ),
        )

    @staticmethod
    def _render(
        sections: tuple[ConversationContextSection, ...],
    ) -> str:
        return "\n\n".join(
            (
                f"[{section.name}]\n"
                f"{section.text.strip()}"
            )
            for section in sections
        )
