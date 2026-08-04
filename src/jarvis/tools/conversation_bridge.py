from __future__ import annotations

from jarvis.core.logger import log
from jarvis.services.ai_service import AIService
from jarvis.tools.openai_runner import (
    OpenAIToolCallingRunner,
)


class ToolCallingConversationBridge:
    def __init__(
        self,
        *,
        runner: OpenAIToolCallingRunner,
        fallback_ai: AIService,
    ) -> None:
        self._runner = runner
        self._fallback_ai = fallback_ai

    async def ask(
        self,
        *,
        text: str,
        history: list[dict[str, str]] | None = None,
    ) -> str:
        try:
            result = await self._runner.run(
                message=text,
                history=history,
            )

            return result.text

        except Exception:  # noqa: BLE001
            log.exception(
                "Native tool-calling failed; "
                "falling back to standard AI chat"
            )

            return await self._fallback_ai.ask(
                text=text,
                history=history,
            )
