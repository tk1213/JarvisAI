from __future__ import annotations

from dataclasses import dataclass

from jarvis.conversation.diagnostics import ConversationDiagnosticsSnapshot
from jarvis.conversation.operational_metrics import ConversationOperationalSnapshot


@dataclass(slots=True, frozen=True)
class ConversationHealthReport:
    operational: ConversationOperationalSnapshot
    latest_turn: ConversationDiagnosticsSnapshot | None

    @property
    def healthy(self) -> bool:
        return self.operational.healthy


class ConversationHealthReporter:
    """Combine latest diagnostics and operational metrics into one report."""

    def build(
        self,
        *,
        operational: ConversationOperationalSnapshot,
        latest_turn: ConversationDiagnosticsSnapshot | None,
    ) -> ConversationHealthReport:
        return ConversationHealthReport(
            operational=operational,
            latest_turn=latest_turn,
        )
