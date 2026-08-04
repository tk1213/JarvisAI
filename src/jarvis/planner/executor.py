from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from time import monotonic
from typing import Any

from jarvis.planner.backoff import BackoffPolicy
from jarvis.planner.bulkhead import (
    BulkheadRejectedError,
    CapabilityBulkhead,
)
from jarvis.planner.circuit_breaker import CircuitBreaker
from jarvis.planner.context import ExecutionContext
from jarvis.planner.deadline import PlanDeadlinePolicy
from jarvis.planner.failures import FailureClassifier
from jarvis.planner.journal import (
    ExecutionEvent,
    ExecutionEventType,
    ExecutionJournal,
)
from jarvis.planner.models import (
    Plan,
    PlanStatus,
    PlanStep,
    PlanStepStatus,
)
from jarvis.planner.references import StepValueResolver
from jarvis.planner.retry import RetryDecision, RetryPolicy
from jarvis.planner.timeout import ExecutionTimeoutPolicy
from jarvis.services.capability import CapabilityRequest
from jarvis.services.capability_router import CapabilityRouter


@dataclass(slots=True)
class PlanStepResult:
    step_index: int
    capability: str
    status: PlanStepStatus
    output: Any = None
    error: str | None = None
    attempts: int = 1

    @property
    def success(self) -> bool:
        return self.status is PlanStepStatus.COMPLETED


@dataclass(slots=True)
class PlanExecutionResult:
    plan: Plan
    step_results: list[PlanStepResult] = field(
        default_factory=list
    )
    journal_events: tuple[ExecutionEvent, ...] = ()

    @property
    def success(self) -> bool:
        return self.plan.status is PlanStatus.COMPLETED

    @property
    def completed_steps(self) -> int:
        return sum(
            result.status is PlanStepStatus.COMPLETED
            for result in self.step_results
        )


class PlanExecutor:
    def __init__(
        self,
        router: CapabilityRouter,
        *,
        value_resolver: StepValueResolver | None = None,
        retry_policy: RetryPolicy | None = None,
        failure_classifier: FailureClassifier | None = None,
        backoff_policy: BackoffPolicy | None = None,
        timeout_policy: ExecutionTimeoutPolicy | None = None,
        deadline_policy: PlanDeadlinePolicy | None = None,
        circuit_breaker: CircuitBreaker | None = None,
        bulkhead: CapabilityBulkhead | None = None,
    ) -> None:
        self._router = router
        self._value_resolver = (
            value_resolver
            if value_resolver is not None
            else StepValueResolver()
        )
        self._retry_policy = (
            retry_policy
            if retry_policy is not None
            else RetryPolicy()
        )
        self._failure_classifier = (
            failure_classifier
            if failure_classifier is not None
            else FailureClassifier()
        )
        self._backoff_policy = (
            backoff_policy
            if backoff_policy is not None
            else BackoffPolicy()
        )
        self._timeout_policy = (
            timeout_policy
            if timeout_policy is not None
            else ExecutionTimeoutPolicy()
        )
        self._deadline_policy = (
            deadline_policy
            if deadline_policy is not None
            else PlanDeadlinePolicy()
        )
        self._circuit_breaker = (
            circuit_breaker
            if circuit_breaker is not None
            else CircuitBreaker()
        )
        self._bulkhead = (
            bulkhead
            if bulkhead is not None
            else CapabilityBulkhead()
        )

    async def execute(
        self,
        plan: Plan,
    ) -> PlanExecutionResult:
        if plan.status is not PlanStatus.READY:
            raise ValueError(
                "Plan must be in READY status before execution."
            )

        context = ExecutionContext()
        journal = ExecutionJournal()
        results: list[PlanStepResult] = []

        deadline = (
            monotonic()
            + self._deadline_policy.plan_timeout_seconds
        )

        plan.status = PlanStatus.RUNNING

        journal.record(
            ExecutionEventType.PLAN_STARTED,
            details={
                "goal": plan.goal,
                "step_count": len(plan.steps),
                "deadline_seconds": (
                    self._deadline_policy.plan_timeout_seconds
                ),
            },
        )

        try:
            for step in plan.steps:
                if deadline - monotonic() <= 0:
                    return self._deadline_failure(
                        plan=plan,
                        results=results,
                        journal=journal,
                        step=step,
                    )

                result = await self._execute_step(
                    step,
                    context=context,
                    journal=journal,
                    deadline=deadline,
                )

                results.append(
                    result
                )

                if result.status is PlanStepStatus.FAILED:
                    plan.status = PlanStatus.FAILED

                    self._skip_remaining_steps(
                        plan,
                        after_index=step.index,
                    )

                    journal.record(
                        ExecutionEventType.PLAN_FAILED,
                        step_index=step.index,
                        capability=step.capability,
                        details={
                            "error": result.error,
                        },
                    )

                    return PlanExecutionResult(
                        plan=plan,
                        step_results=results,
                        journal_events=journal.events,
                    )

                context.set_output(
                    step.index,
                    result.output,
                )

        except asyncio.CancelledError:
            plan.status = PlanStatus.CANCELLED

            for step in plan.steps:
                if step.status is PlanStepStatus.RUNNING:
                    step.status = PlanStepStatus.FAILED
                elif step.status is PlanStepStatus.PENDING:
                    step.status = PlanStepStatus.SKIPPED

            raise

        plan.status = PlanStatus.COMPLETED

        journal.record(
            ExecutionEventType.PLAN_COMPLETED,
            details={
                "completed_steps": len(results),
            },
        )

        return PlanExecutionResult(
            plan=plan,
            step_results=results,
            journal_events=journal.events,
        )

    async def _execute_step(
        self,
        step: PlanStep,
        *,
        context: ExecutionContext,
        journal: ExecutionJournal,
        deadline: float,
    ) -> PlanStepResult:
        step.status = PlanStepStatus.RUNNING

        journal.record(
            ExecutionEventType.STEP_STARTED,
            step_index=step.index,
            capability=step.capability,
            attempt=1,
        )

        if not self._circuit_breaker.allow_request(
            step.capability
        ):
            step.status = PlanStepStatus.FAILED

            error = (
                "capability circuit breaker is open"
            )

            journal.record(
                ExecutionEventType.STEP_FAILED,
                step_index=step.index,
                capability=step.capability,
                attempt=1,
                details={
                    "error": error,
                    "phase": "circuit_breaker",
                },
            )

            return PlanStepResult(
                step_index=step.index,
                capability=step.capability,
                status=step.status,
                error=error,
                attempts=1,
            )

        try:
            arguments = (
                self._value_resolver.resolve_arguments(
                    step.arguments,
                    context=context,
                )
            )
        except Exception as exc:  # noqa: BLE001
            step.status = PlanStepStatus.FAILED

            journal.record(
                ExecutionEventType.STEP_FAILED,
                step_index=step.index,
                capability=step.capability,
                attempt=1,
                details={
                    "error": str(exc),
                    "phase": "argument_resolution",
                },
            )

            return PlanStepResult(
                step_index=step.index,
                capability=step.capability,
                status=step.status,
                error=str(exc),
                attempts=1,
            )

        attempt = 1

        while True:
            remaining = deadline - monotonic()

            if remaining <= 0:
                step.status = PlanStepStatus.FAILED
                error = "plan execution deadline exceeded"

                journal.record(
                    ExecutionEventType.STEP_FAILED,
                    step_index=step.index,
                    capability=step.capability,
                    attempt=attempt,
                    details={
                        "error": error,
                        "phase": "plan_deadline",
                    },
                )

                return PlanStepResult(
                    step_index=step.index,
                    capability=step.capability,
                    status=step.status,
                    error=error,
                    attempts=attempt,
                )

            attempt_timeout = min(
                self._timeout_policy.step_timeout_seconds,
                remaining,
            )

            acquired = False

            try:
                await self._bulkhead.acquire(
                    step.capability
                )
                acquired = True

                request = CapabilityRequest(
                    capability=step.capability,
                    arguments=arguments,
                )

                output = await asyncio.wait_for(
                    self._router.execute_request(
                        request
                    ),
                    timeout=attempt_timeout,
                )

            except BulkheadRejectedError as exc:
                step.status = PlanStepStatus.FAILED

                journal.record(
                    ExecutionEventType.STEP_FAILED,
                    step_index=step.index,
                    capability=step.capability,
                    attempt=attempt,
                    details={
                        "error": str(exc),
                        "phase": "bulkhead",
                    },
                )

                return PlanStepResult(
                    step_index=step.index,
                    capability=step.capability,
                    status=step.status,
                    error=str(exc),
                    attempts=attempt,
                )

            except TimeoutError:
                is_plan_deadline = (
                    deadline - monotonic()
                ) <= 0

                timeout_error = RuntimeError(
                    "plan execution deadline exceeded"
                    if is_plan_deadline
                    else "capability execution timed out"
                )

                classification = (
                    self._failure_classifier.classify(
                        timeout_error
                    )
                )

                if is_plan_deadline:
                    decision = RetryDecision.FAIL
                else:
                    decision = (
                        self._retry_policy.decide_for_capability(
                            capability=step.capability,
                            attempt=attempt,
                            classification=classification,
                        )
                    )

                if decision is RetryDecision.RETRY:
                    delay = (
                        self._backoff_policy.delay_for_retry(
                            attempt=attempt
                        )
                    )

                    if delay >= (
                        deadline - monotonic()
                    ):
                        decision = RetryDecision.FAIL

                if decision is RetryDecision.RETRY:
                    journal.record(
                        ExecutionEventType.STEP_RETRYING,
                        step_index=step.index,
                        capability=step.capability,
                        attempt=attempt,
                        details={
                            "error": str(timeout_error),
                            "failure_kind": (
                                classification.kind.value
                            ),
                            "delay_seconds": delay,
                        },
                    )

                    if delay > 0:
                        await asyncio.sleep(
                            delay
                        )

                    attempt += 1
                    continue

                self._circuit_breaker.record_failure(
                    step.capability
                )
                step.status = PlanStepStatus.FAILED

                journal.record(
                    ExecutionEventType.STEP_FAILED,
                    step_index=step.index,
                    capability=step.capability,
                    attempt=attempt,
                    details={
                        "error": str(timeout_error),
                        "failure_kind": (
                            classification.kind.value
                        ),
                        "phase": (
                            "plan_deadline"
                            if is_plan_deadline
                            else "capability_execution"
                        ),
                    },
                )

                return PlanStepResult(
                    step_index=step.index,
                    capability=step.capability,
                    status=step.status,
                    error=str(timeout_error),
                    attempts=attempt,
                )

            except Exception as exc:  # noqa: BLE001
                classification = (
                    self._failure_classifier.classify(
                        exc
                    )
                )

                decision = (
                    self._retry_policy.decide_for_capability(
                        capability=step.capability,
                        attempt=attempt,
                        classification=classification,
                    )
                )

                if decision is RetryDecision.RETRY:
                    delay = (
                        self._backoff_policy.delay_for_retry(
                            attempt=attempt
                        )
                    )

                    if delay >= (
                        deadline - monotonic()
                    ):
                        decision = RetryDecision.FAIL

                if decision is RetryDecision.RETRY:
                    journal.record(
                        ExecutionEventType.STEP_RETRYING,
                        step_index=step.index,
                        capability=step.capability,
                        attempt=attempt,
                        details={
                            "error": str(exc),
                            "failure_kind": (
                                classification.kind.value
                            ),
                            "delay_seconds": delay,
                        },
                    )

                    if delay > 0:
                        await asyncio.sleep(
                            delay
                        )

                    attempt += 1
                    continue

                self._circuit_breaker.record_failure(
                    step.capability
                )
                step.status = PlanStepStatus.FAILED

                journal.record(
                    ExecutionEventType.STEP_FAILED,
                    step_index=step.index,
                    capability=step.capability,
                    attempt=attempt,
                    details={
                        "error": str(exc),
                        "failure_kind": (
                            classification.kind.value
                        ),
                        "phase": "capability_execution",
                    },
                )

                return PlanStepResult(
                    step_index=step.index,
                    capability=step.capability,
                    status=step.status,
                    error=str(exc),
                    attempts=attempt,
                )

            finally:
                if acquired:
                    self._bulkhead.release(
                        step.capability
                    )

            self._circuit_breaker.record_success(
                step.capability
            )
            step.status = PlanStepStatus.COMPLETED

            journal.record(
                ExecutionEventType.STEP_COMPLETED,
                step_index=step.index,
                capability=step.capability,
                attempt=attempt,
            )

            return PlanStepResult(
                step_index=step.index,
                capability=step.capability,
                status=step.status,
                output=output,
                attempts=attempt,
            )

    def _deadline_failure(
        self,
        *,
        plan: Plan,
        results: list[PlanStepResult],
        journal: ExecutionJournal,
        step: PlanStep,
    ) -> PlanExecutionResult:
        plan.status = PlanStatus.FAILED
        step.status = PlanStepStatus.FAILED

        result = PlanStepResult(
            step_index=step.index,
            capability=step.capability,
            status=step.status,
            error="plan execution deadline exceeded",
            attempts=1,
        )

        results.append(
            result
        )

        self._skip_remaining_steps(
            plan,
            after_index=step.index,
        )

        journal.record(
            ExecutionEventType.STEP_FAILED,
            step_index=step.index,
            capability=step.capability,
            attempt=1,
            details={
                "error": result.error,
                "phase": "plan_deadline",
            },
        )
        journal.record(
            ExecutionEventType.PLAN_FAILED,
            step_index=step.index,
            capability=step.capability,
            details={
                "error": result.error,
            },
        )

        return PlanExecutionResult(
            plan=plan,
            step_results=results,
            journal_events=journal.events,
        )

    @staticmethod
    def _skip_remaining_steps(
        plan: Plan,
        *,
        after_index: int,
    ) -> None:
        for step in plan.steps:
            if (
                step.index > after_index
                and step.status is PlanStepStatus.PENDING
            ):
                step.status = PlanStepStatus.SKIPPED
