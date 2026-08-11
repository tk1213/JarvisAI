from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class ConversationExecutionPolicy:
    timeout_seconds: float = 60.0

    def __post_init__(self) -> None:
        if self.timeout_seconds <= 0:
            raise ValueError(
                "timeout_seconds must be greater than zero."
            )


class ConversationExecutionBoundary:
    """Applies timeout and cancellation boundaries to one conversation turn."""

    def __init__(
        self,
        policy: ConversationExecutionPolicy | None = None,
    ) -> None:
        self._policy = (
            policy
            if policy is not None
            else ConversationExecutionPolicy()
        )

    @property
    def policy(self) -> ConversationExecutionPolicy:
        return self._policy

    async def run(
        self,
        handler: Callable[[], Awaitable[str]],
    ) -> str:
        try:
            async with asyncio.timeout(
                self._policy.timeout_seconds
            ):
                return await handler()
        except TimeoutError as exc:
            raise TimeoutError(
                "Conversation turn exceeded "
                f"{self._policy.timeout_seconds:g} seconds."
            ) from exc
        except asyncio.CancelledError:
            raise
