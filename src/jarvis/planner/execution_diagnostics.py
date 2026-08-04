from __future__ import annotations

from dataclasses import dataclass

from jarvis.planner.execution_detail import (
    ExecutionDetail,
    ExecutionDetailService,
)


@dataclass(slots=True, frozen=True)
class ExecutionDiagnostics:
    record_id: int
    goal: str
    plan_status: str
    failed_steps: tuple[str, ...]
    retry_steps: tuple[str, ...]
    timeout_steps: tuple[str, ...]
    failure_messages: tuple[str, ...]
    event_types: tuple[str, ...]

    @property
    def has_failures(self) -> bool:
        return bool(
            self.failed_steps
        )

    @property
    def has_retries(self) -> bool:
        return bool(
            self.retry_steps
        )

    @property
    def has_timeouts(self) -> bool:
        return bool(
            self.timeout_steps
        )


class ExecutionDiagnosticsService:
    def __init__(
        self,
        detail_service: ExecutionDetailService,
    ) -> None:
        self._detail_service = detail_service

    async def diagnose(
        self,
        record_id: int,
    ) -> ExecutionDiagnostics | None:
        detail = await self._detail_service.get(
            record_id
        )

        if detail is None:
            return None

        return self._build(
            detail
        )

    @staticmethod
    def _build(
        detail: ExecutionDetail,
    ) -> ExecutionDiagnostics:
        failed_steps = tuple(
            step.capability
            for step in detail.steps
            if step.status == "failed"
        )

        retry_steps = tuple(
            step.capability
            for step in detail.steps
            if step.attempts > 1
        )

        timeout_steps = tuple(
            step.capability
            for step in detail.steps
            if (
                step.error is not None
                and "timed out" in step.error.lower()
            )
        )

        failure_messages = tuple(
            step.error
            for step in detail.steps
            if step.error is not None
        )

        event_types = tuple(
            event.event_type
            for event in detail.timeline
        )

        return ExecutionDiagnostics(
            record_id=detail.record_id,
            goal=detail.goal,
            plan_status=detail.plan_status,
            failed_steps=failed_steps,
            retry_steps=retry_steps,
            timeout_steps=timeout_steps,
            failure_messages=failure_messages,
            event_types=event_types,
        )
