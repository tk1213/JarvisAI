import json
from datetime import UTC, datetime

from jarvis.planner.execution_record import (
    ExecutionEventRecord,
    PlanExecutionRecord,
    StepExecutionRecord,
)
from jarvis.planner.execution_record_json import (
    PlanExecutionRecordJSONEncoder,
)


def test_record_can_be_serialized_to_json() -> None:
    record = PlanExecutionRecord(
        goal="Ping Jarvis",
        plan_status="completed",
        success=True,
        completed_steps=1,
        steps=(
            StepExecutionRecord(
                step_index=1,
                capability="system.ping",
                status="completed",
                attempts=1,
                output={
                    "status": "ok",
                },
            ),
        ),
        events=(
            ExecutionEventRecord(
                sequence=1,
                event_type="plan_started",
                timestamp=datetime(
                    2026,
                    8,
                    4,
                    12,
                    0,
                    tzinfo=UTC,
                ),
                step_index=None,
                capability=None,
                attempt=None,
                details={},
            ),
        ),
    )

    payload = PlanExecutionRecordJSONEncoder().dumps(
        record
    )

    data = json.loads(
        payload
    )

    assert data["goal"] == "Ping Jarvis"
    assert data["success"] is True
    assert data["steps"][0]["capability"] == "system.ping"
    assert (
        data["events"][0]["timestamp"]
        == "2026-08-04T12:00:00+00:00"
    )
