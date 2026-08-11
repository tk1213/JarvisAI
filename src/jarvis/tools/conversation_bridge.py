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
        self._last_used_fallback = False

    @property
    def last_used_fallback(self) -> bool:
        return self._last_used_fallback

    async def ask(
        self,
        *,
        text: str,
        history: list[dict[str, str]] | None = None,
        voice_mode: bool = False,
    ) -> str:
        self._last_used_fallback = False

        try:
            if voice_mode:
                result = await self._runner.run(
                    message=text,
                    history=history,
                    voice_mode=True,
                )
            else:
                result = await self._runner.run(
                    message=text,
                    history=history,
                )

            return result.text

        except Exception:  # noqa: BLE001
            self._last_used_fallback = True

            log.exception(
                "Native tool-calling failed; "
                "falling back to standard AI chat"
            )

            if voice_mode:
                return await self._fallback_ai.ask(
                    text=text,
                    history=history,
                    voice_mode=True,
                )

            return await self._fallback_ai.ask(
                text=text,
                history=history,
            )