from __future__ import annotations

import asyncio
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from uuid import uuid4

from jarvis.conversation.reliability import (
    ConversationFailureClassifier,
    ConversationReliabilityOutcome,
)


class ConversationTurnSource(StrEnum):
    AI_AGENT = "ai_agent"
    PLANNER = "planner"
    NATIVE_TOOL = "native_tool"
    CAPABILITY = "capability"
    SMART_HOME = "smart_home"
    SYSTEM = "system"
    FALLBACK_AI = "fallback_ai"
    UNKNOWN = "unknown"


class ConversationTurnStatus(StrEnum):
    COMPLETED = "completed"
    EMPTY = "empty"
    FAILED = "failed"


@dataclass(slots=True, frozen=True)
class ConversationTurnResult:
    user_text: str
    reply: str
    source: ConversationTurnSource
    status: ConversationTurnStatus
    duration_ms: float
    error_type: str | None = None
    turn_id: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    reliability: ConversationReliabilityOutcome | None = None
    recovery_execution: object | None = None

    @property
    def success(self) -> bool:
        return self.status is ConversationTurnStatus.COMPLETED

    @property
    def failed(self) -> bool:
        return self.status is ConversationTurnStatus.FAILED


class ConversationTurnLifecycle:
    """Tracks bounded production turn history and failure classification."""

    def __init__(
        self,
        *,
        clock: Callable[[], float] = time.perf_counter,
        now: Callable[[], datetime] | None = None,
        max_history: int = 100,
        failure_classifier: ConversationFailureClassifier | None = None,
    ) -> None:
        if max_history < 1:
            raise ValueError(
                "max_history must be at least 1."
            )

        self._clock = clock
        self._now = now if now is not None else lambda: datetime.now(UTC)
        self._max_history = max_history
        self._failure_classifier = (
            failure_classifier
            if failure_classifier is not None
            else ConversationFailureClassifier()
        )
        self._last_result: ConversationTurnResult | None = None
        self._active_source: ConversationTurnSource | None = None
        self._history: list[ConversationTurnResult] = []

    @property
    def last_result(self) -> ConversationTurnResult | None:
        return self._last_result

    @property
    def active_source(self) -> ConversationTurnSource | None:
        return self._active_source

    @property
    def max_history(self) -> int:
        return self._max_history

    def list_recent(
        self,
        *,
        limit: int = 20,
    ) -> tuple[ConversationTurnResult, ...]:
        if limit < 1:
            raise ValueError(
                "limit must be at least 1."
            )

        return tuple(
            reversed(
                self._history[-limit:]
            )
        )

    def mark_source(
        self,
        source: ConversationTurnSource,
    ) -> None:
        self._active_source = source

    def empty(
        self,
        user_text: str,
    ) -> ConversationTurnResult:
        timestamp = self._aware_now()

        result = ConversationTurnResult(
            user_text=user_text,
            reply="",
            source=ConversationTurnSource.UNKNOWN,
            status=ConversationTurnStatus.EMPTY,
            duration_ms=0.0,
            turn_id=self._new_turn_id(),
            started_at=timestamp,
            completed_at=timestamp,
        )

        self._record(
            result
        )
        return result

    async def run(
        self,
        *,
        user_text: str,
        source: ConversationTurnSource,
        handler: Callable[[], Awaitable[str]],
    ) -> ConversationTurnResult:
        started_clock = self._clock()
        started_at = self._aware_now()
        turn_id = self._new_turn_id()
        self._active_source = source

        try:
            reply = await handler()

        except asyncio.CancelledError:
            self._active_source = None
            raise

        except Exception as exc:
            failure = self._failure_classifier.classify(
                exc
            )
            result = ConversationTurnResult(
                user_text=user_text,
                reply="",
                source=self._active_source or source,
                status=ConversationTurnStatus.FAILED,
                duration_ms=self._duration_ms(
                    started_clock
                ),
                error_type=type(exc).__name__,
                turn_id=turn_id,
                started_at=started_at,
                completed_at=self._aware_now(),
                reliability=ConversationReliabilityOutcome(
                    failure=failure
                ),
            )

            self._active_source = None
            self._record(
                result
            )
            raise

        result = ConversationTurnResult(
            user_text=user_text,
            reply=reply,
            source=self._active_source or source,
            status=ConversationTurnStatus.COMPLETED,
            duration_ms=self._duration_ms(
                started_clock
            ),
            turn_id=turn_id,
            started_at=started_at,
            completed_at=self._aware_now(),
        )

        self._active_source = None
        self._record(
            result
        )
        return result

    def mark_recovery_execution(
        self,
        execution: object,
    ) -> None:
        if self._last_result is None:
            return

        updated = ConversationTurnResult(
            user_text=self._last_result.user_text,
            reply=self._last_result.reply,
            source=self._last_result.source,
            status=self._last_result.status,
            duration_ms=self._last_result.duration_ms,
            error_type=self._last_result.error_type,
            turn_id=self._last_result.turn_id,
            started_at=self._last_result.started_at,
            completed_at=self._last_result.completed_at,
            reliability=self._last_result.reliability,
            recovery_execution=execution,
        )

        self._last_result = updated

        if self._history:
            self._history[-1] = updated

    def clear_history(
        self,
    ) -> None:
        self._history.clear()
        self._last_result = None

    def _record(
        self,
        result: ConversationTurnResult,
    ) -> None:
        self._last_result = result
        self._history.append(
            result
        )

        overflow = len(self._history) - self._max_history

        if overflow > 0:
            del self._history[:overflow]

    def _duration_ms(
        self,
        started_at: float,
    ) -> float:
        duration = (
            self._clock()
            - started_at
        ) * 1000.0

        return max(
            0.0,
            duration,
        )

    def _aware_now(
        self,
    ) -> datetime:
        timestamp = self._now()

        if timestamp.tzinfo is None:
            raise ValueError(
                "turn timestamp must be timezone-aware."
            )

        return timestamp

    @staticmethod
    def _new_turn_id(
    ) -> str:
        return uuid4().hex
