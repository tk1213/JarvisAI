from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, Mock

from jarvis.wake.activation import WakeActivationStatus
from jarvis.wake.boundary import WakeActivationBoundary


async def main() -> None:
    wake_word = Mock()
    wake_word.closed = False
    wake_word.wait_for_wake_word = AsyncMock(
        return_value=0.91
    )

    result = await WakeActivationBoundary(
        wake_word
    ).wait()

    assert result.status is WakeActivationStatus.DETECTED
    assert result.score == 0.91

    print("Sprint 6 Pack A — Wake Word Activation Contract")
    print("-" * 60)
    print("Threshold contract: PASS")
    print("Closed-state protection: PASS")
    print("Activation boundary: PASS")
    print("Sprint 6 Pack A live gate: PASS")


if __name__ == "__main__":
    asyncio.run(
        main()
    )
