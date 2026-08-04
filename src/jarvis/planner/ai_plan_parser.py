from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from jarvis.planner.ai_plan_contract import (
    AIPlanDraft,
    AIPlanStepDraft,
)


class AIPlanParseError(ValueError):
    pass


@dataclass(slots=True, frozen=True)
class AIPlanParser:
    max_steps: int = 20

    def parse(
        self,
        payload: str | dict[str, Any],
    ) -> AIPlanDraft:
        raw = self._normalize_payload(
            payload
        )

        goal = raw.get(
            "goal"
        )
        steps = raw.get(
            "steps"
        )
        reasoning_summary = raw.get(
            "reasoning_summary",
            "",
        )

        if not isinstance(
            goal,
            str,
        ):
            raise AIPlanParseError(
                "AI plan goal must be a string."
            )

        if not isinstance(
            steps,
            list,
        ):
            raise AIPlanParseError(
                "AI plan steps must be a list."
            )

        if not isinstance(
            reasoning_summary,
            str,
        ):
            raise AIPlanParseError(
                "AI plan reasoning_summary must be a string."
            )

        if len(
            steps
        ) > self.max_steps:
            raise AIPlanParseError(
                "AI plan exceeds the maximum step count."
            )

        parsed_steps = tuple(
            self._parse_step(
                step,
                index=index,
            )
            for index, step in enumerate(
                steps,
                start=1,
            )
        )

        try:
            return AIPlanDraft(
                goal=goal,
                steps=parsed_steps,
                reasoning_summary=reasoning_summary,
            )
        except ValueError as exc:
            raise AIPlanParseError(
                str(
                    exc
                )
            ) from exc

    @staticmethod
    def _normalize_payload(
        payload: str | dict[str, Any],
    ) -> dict[str, Any]:
        if isinstance(
            payload,
            dict,
        ):
            return dict(
                payload
            )

        if not isinstance(
            payload,
            str,
        ):
            raise AIPlanParseError(
                "AI plan payload must be JSON text or an object."
            )

        try:
            decoded = json.loads(
                payload
            )
        except json.JSONDecodeError as exc:
            raise AIPlanParseError(
                "AI plan payload is not valid JSON."
            ) from exc

        if not isinstance(
            decoded,
            dict,
        ):
            raise AIPlanParseError(
                "AI plan JSON root must be an object."
            )

        return decoded

    @staticmethod
    def _parse_step(
        raw: Any,
        *,
        index: int,
    ) -> AIPlanStepDraft:
        if not isinstance(
            raw,
            dict,
        ):
            raise AIPlanParseError(
                f"AI plan step {index} must be an object."
            )

        capability = raw.get(
            "capability"
        )
        arguments = raw.get(
            "arguments",
            {},
        )
        description = raw.get(
            "description",
            "",
        )

        if not isinstance(
            capability,
            str,
        ):
            raise AIPlanParseError(
                f"AI plan step {index} capability "
                "must be a string."
            )

        if not isinstance(
            arguments,
            dict,
        ):
            raise AIPlanParseError(
                f"AI plan step {index} arguments "
                "must be an object."
            )

        if not isinstance(
            description,
            str,
        ):
            raise AIPlanParseError(
                f"AI plan step {index} description "
                "must be a string."
            )

        try:
            return AIPlanStepDraft(
                capability=capability,
                arguments=dict(
                    arguments
                ),
                description=description,
            )
        except ValueError as exc:
            raise AIPlanParseError(
                f"AI plan step {index}: {exc}"
            ) from exc
