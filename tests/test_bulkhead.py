from __future__ import annotations

import asyncio

import pytest

from jarvis.planner.bulkhead import (
    BulkheadPolicy,
    BulkheadRejectedError,
    CapabilityBulkhead,
)


@pytest.mark.asyncio
async def test_bulkhead_rejects_when_limit_is_full() -> None:
    bulkhead = CapabilityBulkhead(
        BulkheadPolicy(
            max_concurrent_per_capability=1,
            acquire_timeout_seconds=0.01,
        )
    )

    await bulkhead.acquire(
        "system.ping"
    )

    try:
        with pytest.raises(
            BulkheadRejectedError,
            match="concurrency limit",
        ):
            await bulkhead.acquire(
                "system.ping"
            )
    finally:
        bulkhead.release(
            "system.ping"
        )


@pytest.mark.asyncio
async def test_bulkhead_is_per_capability() -> None:
    bulkhead = CapabilityBulkhead(
        BulkheadPolicy(
            max_concurrent_per_capability=1,
            acquire_timeout_seconds=0.01,
        )
    )

    await bulkhead.acquire(
        "system.ping"
    )

    try:
        await asyncio.wait_for(
            bulkhead.acquire(
                "system.version"
            ),
            timeout=0.05,
        )

        bulkhead.release(
            "system.version"
        )
    finally:
        bulkhead.release(
            "system.ping"
        )
