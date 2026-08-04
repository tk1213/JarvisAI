from jarvis.planner.journal import (
    ExecutionEventType,
    ExecutionJournal,
)
from jarvis.planner.resilience_runtime import (
    resilience_runtime,
)


def test_journal_updates_shared_resilience_runtime() -> None:
    before = (
        resilience_runtime.snapshot()
        .metrics.plans_started
    )

    journal = ExecutionJournal()

    journal.record(
        ExecutionEventType.PLAN_STARTED
    )

    after = (
        resilience_runtime.snapshot()
        .metrics.plans_started
    )

    assert after == before + 1
