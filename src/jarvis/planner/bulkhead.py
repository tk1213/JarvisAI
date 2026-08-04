from __future__ import annotations

import asyncio
from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class BulkheadPolicy:
    max_concurrent_per_capability: int = 2
    acquire_timeout_seconds: float = 1.0

    def __post_init__(self) -> None:
        if self.max_concurrent_per_capability < 1:
            raise ValueError(
                "max_concurrent_per_capability must be at least 1."
            )

        if self.acquire_timeout_seconds <= 0:
            raise ValueError(
                "acquire_timeout_seconds must be greater than 0."
            )


class BulkheadRejectedError(RuntimeError):
    pass


class CapabilityBulkhead:
    def __init__(
        self,
        policy: BulkheadPolicy | None = None,
    ) -> None:
        self._policy = (
            policy
            if policy is not None
            else BulkheadPolicy()
        )
        self._semaphores: dict[
            str,
            asyncio.Semaphore,
        ] = {}

    async def acquire(
        self,
        capability: str,
    ) -> None:
        semaphore = self._get_semaphore(
            capability
        )

        try:
            await asyncio.wait_for(
                semaphore.acquire(),
                timeout=(
                    self._policy.acquire_timeout_seconds
                ),
            )
        except TimeoutError as exc:
            raise BulkheadRejectedError(
                "capability concurrency limit reached"
            ) from exc

    def release(
        self,
        capability: str,
    ) -> None:
        semaphore = self._get_semaphore(
            capability
        )
        semaphore.release()

    def _get_semaphore(
        self,
        capability: str,
    ) -> asyncio.Semaphore:
        key = capability.strip()

        if not key:
            raise ValueError(
                "Capability cannot be empty."
            )

        semaphore = self._semaphores.get(
            key
        )

        if semaphore is None:
            semaphore = asyncio.Semaphore(
                self._policy.max_concurrent_per_capability
            )
            self._semaphores[
                key
            ] = semaphore

        return semaphore
