from datetime import UTC, datetime

import pytest

from jarvis.planner.capability_reliability import (
    CapabilityReliabilityService,
)
from jarvis.planner.execution_record import (
    ExecutionEventRecord,
    PlanExecutionRecord,
    StepExecutionRecord,
)


class FakePersistence:
    def __init__(
        self,
        records: list[PlanExecutionRecord],
    ) -> None:
        self.records = records

    async def list_recent(
        self,
        *,
        limit: int = 100,
    ) -> list[PlanExecutionRecord]:
        return self.records[:limit]


def make_record(
    *,
    capability: str,
    status: str,
    attempts: int = 1,
    error: str | None = None,
) -> PlanExecutionRecord:
    success = status == "completed"

    return PlanExecutionRecord(
        goal=f"Run {capability}",
        plan_status=(
            "completed"
            if success
            else "failed"
        ),
        success=success,
        completed_steps=(
            1
            if success
            else 0
        ),
        steps=(
            StepExecutionRecord(
                step_index=1,
                capability=capability,
                status=status,
                attempts=attempts,
                error=error,
            ),
        ),
        events=(
            ExecutionEventRecord(
                sequence=1,
                event_type="plan_started",
                timestamp=datetime.now(UTC),
                step_index=None,
                capability=None,
                attempt=None,
                details={},
            ),
        ),
    )


@pytest.mark.asyncio
async def test_reliability_aggregates_by_capability() -> None:
    service = CapabilityReliabilityService(
        FakePersistence(
            [
                make_record(
                    capability="system.ping",
                    status="completed",
                ),
                make_record(
                    capability="system.ping",
                    status="failed",
                    attempts=2,
                    error="capability execution timed out",
                ),
                make_record(
                    capability="system.version",
                    status="completed",
                ),
            ]
        )  # type: ignore[arg-type]
    )

    summary = await service.summarize(
        limit=10
    )

    assert summary.total_capabilities == 2

    by_name = {
        item.capability: item
        for item in summary.capabilities
    }

    ping = by_name[
        "system.ping"
    ]

    assert ping.executions == 2
    assert ping.failures == 1
    assert ping.retries == 1
    assert ping.timeouts == 1
    assert ping.success_rate == pytest.approx(
        0.5
    )

    version = by_name[
        "system.version"
    ]

    assert version.executions == 1
    assert version.failures == 0
    assert version.success_rate == pytest.approx(
        1.0
    )


@pytest.mark.asyncio
async def test_reliability_handles_empty_history() -> None:
    service = CapabilityReliabilityService(
        FakePersistence(
            []
        )  # type: ignore[arg-type]
    )

    summary = await service.summarize()

    assert summary.total_capabilities == 0
    assert summary.capabilities == ()


@pytest.mark.asyncio
async def test_reliability_rejects_invalid_limit() -> None:
    service = CapabilityReliabilityService(
        FakePersistence(
            []
        )  # type: ignore[arg-type]
    )

    with pytest.raises(
        ValueError,
        match="at least 1",
    ):
        await service.summarize(
            limit=0
        )
