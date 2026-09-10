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


class APISmartHomeDevice(BaseModel):
    model_config = ConfigDict(
        frozen=True,
    )

    id: str
    name: str
    room: str
    device_type: str
    online: bool
    power: bool


class APISmartHomeDevicesResponse(BaseModel):
    model_config = ConfigDict(
        frozen=True,
    )

    connected: bool
    devices: list[APISmartHomeDevice] = Field(
        default_factory=list,
    )