from jarvis.planner.execution_detail import (
    ExecutionDetail,
    ExecutionStepDetail,
    ExecutionTimelineEntry,
)
from jarvis.planner.execution_diagnostics import (
    ExecutionDiagnosticsService,
)


class FakeDetailService:
    def __init__(
        self,
        detail: ExecutionDetail | None,
    ) -> None:
        self.detail = detail

    async def get(
        self,
        record_id: int,
    ) -> ExecutionDetail | None:
        del record_id
        return self.detail


def make_detail() -> ExecutionDetail:
    return ExecutionDetail(
        record_id=8,
        goal="Diagnose failure",
        plan_status="failed",
        success=False,
        completed_steps=1,
        steps=(
            ExecutionStepDetail(
                step_index=1,
                capability="system.ping",
                status="completed",
                attempts=2,
            ),
            ExecutionStepDetail(
                step_index=2,
                capability="system.version",
                status="failed",
                attempts=1,
                error="invalid request",
            ),
            ExecutionStepDetail(
                step_index=3,
                capability="system.health",
                status="failed",
                attempts=2,
                error="capability execution timed out",
            ),
        ),
        timeline=(
            ExecutionTimelineEntry(
                sequence=1,
                event_type="plan_started",
                timestamp="2026-08-04T12:00:00+00:00",
                step_index=None,
                capability=None,
                attempt=None,
                details={},
            ),
            ExecutionTimelineEntry(
                sequence=2,
                event_type="step_failed",
                timestamp="2026-08-04T12:00:01+00:00",
                step_index=2,
                capability="system.version",
                attempt=1,
                details={
                    "error": "invalid request",
                },
            ),
        ),
        failure_count=2,
    )


async def test_diagnostics_classifies_failures_retries_and_timeouts() -> None:
    service = ExecutionDiagnosticsService(
        FakeDetailService(
            make_detail()
        )  # type: ignore[arg-type]
    )

    diagnostics = await service.diagnose(
        8
    )

    assert diagnostics is not None
    assert diagnostics.failed_steps == (
        "system.version",
        "system.health",
    )
    assert diagnostics.retry_steps == (
        "system.ping",
        "system.health",
    )
    assert diagnostics.timeout_steps == (
        "system.health",
    )
    assert diagnostics.failure_messages == (
        "invalid request",
        "capability execution timed out",
    )
    assert diagnostics.has_failures is True
    assert diagnostics.has_retries is True
    assert diagnostics.has_timeouts is True


async def test_diagnostics_returns_none_for_missing_detail() -> None:
    service = ExecutionDiagnosticsService(
        FakeDetailService(
            None
        )  # type: ignore[arg-type]
    )

    assert await service.diagnose(
        99
    ) is None
