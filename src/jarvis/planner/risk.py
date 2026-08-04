from __future__ import annotations

from enum import StrEnum
from typing import ClassVar


class PlanRiskLevel(StrEnum):
    READ_ONLY = "read_only"
    SIDE_EFFECT = "side_effect"


class PlanRiskPolicy:
    _READ_ONLY_CAPABILITIES: ClassVar[frozenset[str]] = frozenset(
        {
            "smart_home.list_devices",
            "smart_home.status",
            "system.health",
            "system.ping",
            "system.version",
        }
    )

    _READ_ONLY_SUFFIXES: ClassVar[tuple[str, ...]] = (
        ".get",
        ".health",
        ".list",
        ".list_devices",
        ".ping",
        ".read",
        ".status",
        ".version",
    )

    @classmethod
    def classify(
        cls,
        capability: str,
    ) -> PlanRiskLevel:
        normalized = capability.strip().casefold()

        if not normalized:
            return PlanRiskLevel.SIDE_EFFECT

        if normalized in cls._READ_ONLY_CAPABILITIES:
            return PlanRiskLevel.READ_ONLY

        if any(
            normalized.endswith(suffix)
            for suffix in cls._READ_ONLY_SUFFIXES
        ):
            return PlanRiskLevel.READ_ONLY

        return PlanRiskLevel.SIDE_EFFECT
