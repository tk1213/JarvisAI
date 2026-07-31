from abc import ABC, abstractmethod
from collections.abc import AsyncIterator


class BaseAI(ABC):
    @abstractmethod
    async def chat(
        self,
        message: str,
        history: list[dict[str, str]] | None = None,
    ) -> str:
        raise NotImplementedError

    @abstractmethod
    async def stream_chat(
        self,
        message: str,
        history: list[dict[str, str]] | None = None,
    ) -> AsyncIterator[str]:
        raise NotImplementedError