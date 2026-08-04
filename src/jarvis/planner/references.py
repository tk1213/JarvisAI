from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from jarvis.planner.context import ExecutionContext


@dataclass(slots=True, frozen=True)
class StepOutputReference:
    step_index: int
    path: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.step_index < 1:
            raise ValueError(
                "step_index must be at least 1."
            )


class StepValueResolver:
    _REFERENCE_KEY = "$step"

    def resolve_arguments(
        self,
        arguments: dict[str, Any],
        *,
        context: ExecutionContext,
    ) -> dict[str, Any]:
        return {
            key: self.resolve_value(
                value,
                context=context,
            )
            for key, value in arguments.items()
        }

    def resolve_value(
        self,
        value: Any,
        *,
        context: ExecutionContext,
    ) -> Any:
        if isinstance(
            value,
            dict,
        ):
            reference = self._parse_reference(
                value
            )

            if reference is not None:
                return self._resolve_reference(
                    reference,
                    context=context,
                )

            return {
                key: self.resolve_value(
                    nested_value,
                    context=context,
                )
                for key, nested_value in value.items()
            }

        if isinstance(
            value,
            list,
        ):
            return [
                self.resolve_value(
                    item,
                    context=context,
                )
                for item in value
            ]

        return value

    def _parse_reference(
        self,
        value: dict[str, Any],
    ) -> StepOutputReference | None:
        if set(
            value
        ) != {
            self._REFERENCE_KEY
        }:
            return None

        raw_reference = value[
            self._REFERENCE_KEY
        ]

        if not isinstance(
            raw_reference,
            str,
        ):
            raise TypeError(
                "$step reference must be a string."
            )

        parts = [
            part
            for part in raw_reference.split(
                "."
            )
            if part
        ]

        if not parts:
            raise ValueError(
                "$step reference cannot be empty."
            )

        try:
            step_index = int(
                parts[0]
            )
        except ValueError as exc:
            raise ValueError(
                "$step reference must start with a step number."
            ) from exc

        return StepOutputReference(
            step_index=step_index,
            path=tuple(
                parts[1:]
            ),
        )

    @staticmethod
    def _resolve_reference(
        reference: StepOutputReference,
        *,
        context: ExecutionContext,
    ) -> Any:
        value = context.get_output(
            reference.step_index
        )

        for part in reference.path:
            if not isinstance(
                value,
                dict,
            ):
                raise TypeError(
                    "Cannot resolve nested step output path "
                    f"at {part!r}."
                )

            if part not in value:
                raise KeyError(
                    "Step output path not found: "
                    f"{part}"
                )

            value = value[
                part
            ]

        return value
