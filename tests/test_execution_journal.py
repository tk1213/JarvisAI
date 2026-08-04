from jarvis.planner.journal import (
    ExecutionEventType,
    ExecutionJournal,
)


def test_journal_records_sequential_events() -> None:
    journal = ExecutionJournal()

    first = journal.record(
        ExecutionEventType.PLAN_STARTED
    )

    second = journal.record(
        ExecutionEventType.STEP_STARTED,
        step_index=1,
        capability="system.ping",
        attempt=1,
    )

    assert first.sequence == 1
    assert second.sequence == 2
    assert len(journal.events) == 2


def test_journal_events_are_exposed_as_tuple() -> None:
    journal = ExecutionJournal()

    journal.record(
        ExecutionEventType.PLAN_STARTED
    )

    assert isinstance(
        journal.events,
        tuple,
    )
