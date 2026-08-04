from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ExecutionContext:
    """
    Runtime state shared across steps in one plan execution.

    Step outputs are stored by step index and can be referenced by later
    steps without changing the original Plan model.
    """

    step_outputs: dict[int, Any] = field(
        default_factory=dict
    )

    def set_output(
        self,
        step_index: int,
        output: Any,
    ) -> None:
        if step_index < 1:
            raise ValueError(
                "step_index must be at least 1."
            )

        self.step_outputs[
            step_index
        ] = output

    def get_output(
        self,
        step_index: int,
    ) -> Any:
        if step_index < 1:
            raise ValueError(
                "step_index must be at least 1."
            )

        if step_index not in self.step_outputs:
            raise KeyError(
                f"No output stored for step {step_index}."
            )

        return self.step_outputs[
            step_index
        ]

    def has_output(
        self,
        step_index: int,
    ) -> bool:
        return step_index in self.step_outputs
