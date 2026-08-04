from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class ExecutionQuery:
    limit: int = 20
    status: str | None = None
    capability: str | None = None

    def __post_init__(self) -> None:
        if self.limit < 1:
            raise ValueError(
                "limit must be at least 1."
            )

        if self.status is not None:
            normalized_status = self.status.strip().lower()

            if not normalized_status:
                raise ValueError(
                    "status cannot be empty."
                )

            object.__setattr__(
                self,
                "status",
                normalized_status,
            )

        if self.capability is not None:
            normalized_capability = self.capability.strip()

            if not normalized_capability:
                raise ValueError(
                    "capability cannot be empty."
                )

            object.__setattr__(
                self,
                "capability",
                normalized_capability,
            )
