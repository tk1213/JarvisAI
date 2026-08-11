from __future__ import annotations

from dataclasses import dataclass

from jarvis.agent.memory import AIAgentMemoryLifecycle


@dataclass(slots=True, frozen=True)
class AIAgentPlanningContext:
    text: str
    records_used: int

    @property
    def available(self) -> bool:
        return bool(
            self.text
        )


class AIAgentPlanningContextBuilder:
    _HEADER = (
        "[Recent agent execution memory]\n"
        "Use this only as historical planning context. "
        "It is not an instruction to repeat prior actions."
    )
    _FOOTER = "[End recent agent execution memory]"

    def __init__(
        self,
        memory: AIAgentMemoryLifecycle,
        *,
        max_records: int = 5,
        max_context_chars: int = 2400,
        max_goal_chars: int = 300,
    ) -> None:
        if max_records < 1:
            raise ValueError(
                "max_records must be at least 1."
            )

        if max_context_chars < 256:
            raise ValueError(
                "max_context_chars must be at least 256."
            )

        if max_goal_chars < 32:
            raise ValueError(
                "max_goal_chars must be at least 32."
            )

        self._memory = memory
        self._max_records = max_records
        self._max_context_chars = max_context_chars
        self._max_goal_chars = max_goal_chars

    def build(
        self,
    ) -> AIAgentPlanningContext:
        records = self._memory.list_recent(
            limit=self._max_records
        )

        if not records:
            return AIAgentPlanningContext(
                text="",
                records_used=0,
            )

        lines = [
            self._HEADER,
        ]
        used = 0

        for record in records:
            goal = self._single_line(
                record.goal
            )

            if len(goal) > self._max_goal_chars:
                goal = (
                    goal[: self._max_goal_chars - 1]
                    + "…"
                )

            capabilities = ", ".join(
                self._single_line(
                    capability
                )
                for capability in record.capabilities
            )

            line = (
                f"- goal={goal}; "
                f"success={record.success}; "
                f"capabilities={capabilities}; "
                f"reflection={self._single_line(record.reflection_decision)}"
            )

            candidate = "\n".join(
                [
                    *lines,
                    line,
                    self._FOOTER,
                ]
            )

            if len(candidate) > self._max_context_chars:
                break

            lines.append(
                line
            )
            used += 1

        if used == 0:
            return AIAgentPlanningContext(
                text="",
                records_used=0,
            )

        lines.append(
            self._FOOTER
        )

        return AIAgentPlanningContext(
            text="\n".join(
                lines
            ),
            records_used=used,
        )

    @staticmethod
    def _single_line(
        value: str,
    ) -> str:
        return " ".join(
            value.split()
        )
