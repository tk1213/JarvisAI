from __future__ import annotations

from dataclasses import dataclass

from jarvis.planner.execution_diagnostics import (
    ExecutionDiagnostics,
)


@dataclass(slots=True, frozen=True)
class ExecutionDiagnosticsReport:
    summary: str
    lines: tuple[str, ...]


class ExecutionDiagnosticsReportBuilder:
    def build(
        self,
        diagnostics: ExecutionDiagnostics,
    ) -> ExecutionDiagnosticsReport:
        summary = (
            f"Execution {diagnostics.record_id} diagnostics: "
            f"status={diagnostics.plan_status}, "
            f"failed_steps={len(diagnostics.failed_steps)}, "
            f"retry_steps={len(diagnostics.retry_steps)}, "
            f"timeout_steps={len(diagnostics.timeout_steps)}."
        )

        lines: list[str] = []

        if diagnostics.failed_steps:
            lines.append(
                "Failed capabilities: "
                + ", ".join(
                    diagnostics.failed_steps
                )
            )

        if diagnostics.retry_steps:
            lines.append(
                "Retried capabilities: "
                + ", ".join(
                    diagnostics.retry_steps
                )
            )

        if diagnostics.timeout_steps:
            lines.append(
                "Timed out capabilities: "
                + ", ".join(
                    diagnostics.timeout_steps
                )
            )

        if diagnostics.failure_messages:
            lines.append(
                "Failure messages: "
                + " | ".join(
                    diagnostics.failure_messages
                )
            )

        if not lines:
            lines.append(
                "No execution failures, retries, or timeouts detected."
            )

        return ExecutionDiagnosticsReport(
            summary=summary,
            lines=tuple(
                lines
            ),
        )
