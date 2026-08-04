from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from jarvis.smart_home.device import SmartDevice


class DeviceResolutionStatus(str, Enum):
    FOUND = "found"
    NOT_FOUND = "not_found"
    AMBIGUOUS = "ambiguous"


@dataclass(
    slots=True,
    frozen=True,
)
class DeviceResolution:
    status: DeviceResolutionStatus
    device: SmartDevice | None = None
    candidates: tuple[SmartDevice, ...] = ()

    @classmethod
    def found(
        cls,
        device: SmartDevice,
    ) -> DeviceResolution:
        return cls(
            status=DeviceResolutionStatus.FOUND,
            device=device,
            candidates=(device,),
        )

    @classmethod
    def not_found(
        cls,
    ) -> DeviceResolution:
        return cls(
            status=DeviceResolutionStatus.NOT_FOUND,
        )

    @classmethod
    def ambiguous(
        cls,
        devices: list[SmartDevice],
    ) -> DeviceResolution:
        if len(devices) < 2:
            raise ValueError(
                "Ambiguous resolution requires "
                "at least two devices."
            )

        return cls(
            status=DeviceResolutionStatus.AMBIGUOUS,
            candidates=tuple(devices),
        )

    @property
    def is_found(self) -> bool:
        return (
            self.status
            is DeviceResolutionStatus.FOUND
        )

    @property
    def is_not_found(self) -> bool:
        return (
            self.status
            is DeviceResolutionStatus.NOT_FOUND
        )

    @property
    def is_ambiguous(self) -> bool:
        return (
            self.status
            is DeviceResolutionStatus.AMBIGUOUS
        )