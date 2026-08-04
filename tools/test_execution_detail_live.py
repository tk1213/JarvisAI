from __future__ import annotations

import asyncio
import tempfile
from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
)

from jarvis.database.db import DatabaseManager
from jarvis.planner.execution_detail import ExecutionDetailService
from jarvis.planner.execution_detail_report import (
    ExecutionDetailReportBuilder,
)
from jarvis.planner.execution_persistence import (
    ExecutionPersistenceService,
)
from jarvis.planner.execution_record import (
    ExecutionEventRecord,
    PlanExecutionRecord,
    StepExecutionRecord,
)
from jarvis.planner.execution_repository import PlanExecutionRepository


def make_record() -> PlanExecutionRecord:
    return PlanExecutionRecord(
        goal="Inspect persisted execution detail",
        plan_status="failed",
        success=False,
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
            StepExecutionRecord(
                step_index=2,
                capability="system.version",
                status="failed",
                attempts=1,
                error="invalid request",
            ),
        ),
        events=(
            ExecutionEventRecord(
                sequence=1,
                event_type="plan_started",
                timestamp=datetime.now(UTC),
                step_index=None,
                capability=None,
                attempt=None,
                details={},
            ),
            ExecutionEventRecord(
                sequence=2,
                event_type="step_failed",
                timestamp=datetime.now(UTC),
                step_index=2,
                capability="system.version",
                attempt=1,
                details={
                    "error": "invalid request",
                },
            ),
        ),
    )


async def main() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = (
            Path(temp_dir)
            / "execution_detail.db"
        )

        database = DatabaseManager()

        await database.engine.dispose()

        database.engine = create_async_engine(
            (
                "sqlite+aiosqlite:///"
                f"{db_path.as_posix()}"
            ),
            echo=False,
        )
        database.session_factory = async_sessionmaker(
            bind=database.engine,
            expire_on_commit=False,
        )

        try:
            repository = PlanExecutionRepository(
                database
            )
            persistence = ExecutionPersistenceService(
                repository
            )

            await persistence.startup()

            record_id = await repository.save(
                make_record()
            )

            detail_service = ExecutionDetailService(
                persistence
            )

            detail = await detail_service.get(
                record_id
            )

            if detail is None:
                raise RuntimeError(
                    "Execution detail was not found."
                )

            report = ExecutionDetailReportBuilder().build(
                detail
            )

            print(
                "Sprint 3.6 Execution Detail"
            )
            print(
                "-" * 60
            )
            print(
                report.summary
            )

            print()
            print(
                "Steps:"
            )
            for line in report.step_lines:
                print(
                    line
                )

            print()
            print(
                "Timeline:"
            )
            for line in report.timeline_lines:
                print(
                    line
                )

            if detail.failure_count != 1:
                raise RuntimeError(
                    "Execution failure count is incorrect."
                )

            print()
            print(
                "Execution detail gate: PASS"
            )

        finally:
            await database.engine.dispose()


if __name__ == "__main__":
    asyncio.run(
        main()
    )
