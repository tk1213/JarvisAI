from collections.abc import AsyncIterator

from jarvis.ai.base import BaseAI
from jarvis.ai.openai_client import OpenAIClient


class AIService:
    def __init__(self) -> None:
        self.client: BaseAI = OpenAIClient()

    async def ask(
        self,
        text: str,
        history: list[dict[str, str]] | None = None,
        *,
        voice_mode: bool = False,
    ) -> str:
        return await self.client.chat(
            message=text,
            history=history,
            voice_mode=voice_mode,
        )

    async def stream(
        self,
        text: str,
        history: list[dict[str, str]] | None = None,
    ) -> AsyncIterator[str]:
        async for chunk in self.client.stream_chat(
            message=text,
            history=history,
        ):
            yield chunk

    def reset_conversation(self) -> None:
        # AIService ยังไม่มี state ภายในที่ต้อง reset
        return