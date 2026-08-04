from __future__ import annotations

from jarvis.memory.audit import MemoryAuditAction
from jarvis.memory.audit_service import MemoryAuditService
from jarvis.memory.capture_policy import (
    MemoryCaptureDecision,
    MemoryCapturePolicy,
)
from jarvis.memory.extractor import MemoryExtractor
from jarvis.memory.service import MemoryService


class MemoryCaptureService:
    def __init__(
        self,
        *,
        extractor: MemoryExtractor,
        memory: MemoryService,
        policy: MemoryCapturePolicy | None = None,
        audit: MemoryAuditService | None = None,
    ) -> None:
        self._extractor = extractor
        self._memory = memory
        self._policy = (
            policy
            if policy is not None
            else MemoryCapturePolicy()
        )
        self._audit = audit

    async def capture(
        self,
        text: str,
    ) -> int:
        decisions = await self.capture_detailed(
            text
        )

        return sum(
            decision.should_store
            for decision in decisions
        )

    async def capture_detailed(
        self,
        text: str,
    ) -> list[MemoryCaptureDecision]:
        extracted_memories = self._extractor.extract(
            text
        )

        decisions: list[MemoryCaptureDecision] = []

        for extracted in extracted_memories:
            decision = self._policy.evaluate(
                extracted
            )

            decisions.append(
                decision
            )

            if not decision.should_store:
                await self._record_rejection(
                    decision
                )
                continue

            await self._memory.remember(
                category=extracted.category,
                key=extracted.key,
                value=extracted.value,
                importance=extracted.importance,
                source=extracted.source,
            )

        return decisions

    async def _record_rejection(
        self,
        decision: MemoryCaptureDecision,
    ) -> None:
        if self._audit is None:
            return

        memory = decision.memory

        await self._audit.record(
            action=MemoryAuditAction.REJECTED,
            key=memory.key,
            value=memory.value,
            source=memory.source,
            reason=decision.reason,
        )
