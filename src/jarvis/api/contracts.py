from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class APIHealthResponse(BaseModel):
    model_config = ConfigDict(
        frozen=True,
    )

    status: Literal[
        "healthy",
        "degraded",
    ]

    checks: dict[str, bool] = Field(
        default_factory=dict,
    )