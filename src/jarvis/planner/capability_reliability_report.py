from __future__ import annotations

from dataclasses import dataclass

from jarvis.planner.capability_reliability import (
    CapabilityReliabilitySummary,
)


@dataclass(slots=True, frozen=True)
class CapabilityReliabilityReport:
    summary: str
    lines: tuple[str, ...]


class CapabilityReliabilityReportBuilder:
    def build(
        self,
        reliability: CapabilityReliabilitySummary,
    ) -> CapabilityReliabilityReport:
        summary = (
            "Capability reliability: "
            f"{reliability.total_capabilities} "
            "capability record(s)."
        )

        lines = tuple(
            (
                f"{item.capability}: "
                f"executions={item.executions}, "
                f"failures={item.failures}, "
                f"retries={item.retries}, "
                f"timeouts={item.timeouts}, "
                f"success_rate={item.success_rate:.1%}"
            )
            for item in reliability.capabilities
        )

        return CapabilityReliabilityReport(
            summary=summary,
            lines=lines,
        )
