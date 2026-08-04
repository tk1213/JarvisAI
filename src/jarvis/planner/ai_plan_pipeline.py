from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from jarvis.planner.ai_plan_adapter import (
    AIPlanAdaptationResult,
    AIPlanAdapter,
)
from jarvis.planner.ai_plan_contract import AIPlanDraft
from jarvis.planner.ai_plan_parser import AIPlanParser


@dataclass(slots=True, frozen=True)
class AIPlanPipelineResult:
    draft: AIPlanDraft
    adaptation: AIPlanAdaptationResult


class AIPlanPipeline:
    def __init__(
        self,
        *,
        parser: AIPlanParser,
        adapter: AIPlanAdapter,
    ) -> None:
        self._parser = parser
        self._adapter = adapter

    def build(
        self,
        payload: str | dict[str, Any],
    ) -> AIPlanPipelineResult:
        draft = self._parser.parse(
            payload
        )

        adaptation = self._adapter.adapt(
            draft
        )

        return AIPlanPipelineResult(
            draft=draft,
            adaptation=adaptation,
        )
