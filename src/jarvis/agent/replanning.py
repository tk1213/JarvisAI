from __future__ import annotations

from dataclasses import dataclass

from jarvis.planner.ai_plan_reflection import (
    AIPlanReflectionDecision,
    AIPlanReflectionResult,
)


@dataclass(slots=True, frozen=True)
class AIAgentReplanPolicy:
    max_replans: int = 1
    max_context_chars: int = 1200

    def __post_init__(self) -> None:
        if self.max_replans < 0:
            raise ValueError(
                "max_replans cannot be negative."
            )

        if self.max_context_chars < 256:
            raise ValueError(
                "max_context_chars must be at least 256."
            )

    def should_replan(
        self,
        *,
        reflection: AIPlanReflectionResult,
        attempts: int,
    ) -> bool:
        return (
            reflection.decision
            is AIPlanReflectionDecision.RETRY
            and attempts < self.max_replans
        )

    def build_retry_text(
        self,
        *,
        original_text: str,
        reflection: AIPlanReflectionResult,
        attempt: int,
    ) -> str:
        findings = []

        for finding in reflection.findings:
            message = " ".join(
                finding.message.split()
            )

            findings.append(
                f"- {finding.code}: {message}"
            )

        reflection_text = "\n".join(
            findings
        )

        retry_context = (
            "[Agent retry context]\n"
            "The previous read-only plan failed with transient errors. "
            "Use this only to improve a new plan. "
            "Do not repeat a side-effect action automatically.\n"
            f"Retry attempt: {attempt}\n"
            f"{reflection_text}\n"
            "[End agent retry context]"
        )

        available = (
            self.max_context_chars
            - len(original_text)
            - 2
        )

        if available < 1:
            return original_text

        if len(retry_context) > available:
            retry_context = retry_context[:available]

        return (
            f"{original_text}\n\n"
            f"{retry_context}"
        )
