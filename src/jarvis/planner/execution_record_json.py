from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime
from typing import Any

from jarvis.planner.execution_record import PlanExecutionRecord


class PlanExecutionRecordJSONEncoder:
    def dumps(
        self,
        record: PlanExecutionRecord,
        *,
        indent: int | None = None,
    ) -> str:
        return json.dumps(
            asdict(
                record
            ),
            ensure_ascii=False,
            indent=indent,
            default=self._default,
        )

    @staticmethod
    def _default(
        value: Any,
    ) -> Any:
        if isinstance(
            value,
            datetime,
        ):
            return value.isoformat()

        raise TypeError(
            "Object is not JSON serializable: "
            f"{type(value).__name__}"
        )
