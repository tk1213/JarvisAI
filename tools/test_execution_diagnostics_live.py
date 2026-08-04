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
from jarvis.planner.execution_diagnostics import (
    ExecutionDiagnosticsService,
)
from jarvis.planner.execution_diagnostics_report import (
    ExecutionDiagnosticsReportBuilder,
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
        goal="Diagnose persisted execution",
        plan_status="failed",
        success=False,
        completed_steps=1,
        steps=(
            StepExecutionRecord(
                step_index=1,
                capability="system.ping",
                status="completed",
                attempts=2,
            ),
            StepExecutionRecord(
                step_index=2,
                capability="system.health",
                status="failed",
                attempts=2,
                error="capability execution timed out",
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
                event_type="step_retrying",
                timestamp=datetime.now(UTC),
                step_index=1,
                capability="system.ping",
                attempt=1,
                details={},
            ),
            ExecutionEventRecord(
                sequence=3,
                event_type="step_failed",
                timestamp=datetime.now(UTC),
                step_index=2,
                capability="system.health",
                attempt=2,
                details={
                    "error": "capability execution timed out",
                },
            ),
        ),
    )


async def main() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = (
            Path(temp_dir)
            / "execution_diagnostics.db"
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
            diagnostics_service = ExecutionDiagnosticsService(
                detail_service
            )

            diagnostics = await diagnostics_service.diagnose(
                record_id
            )

            if diagnostics is None:
                raise RuntimeError(
                    "Execution diagnostics were not found."
                )

            report = ExecutionDiagnosticsReportBuilder().build(
                diagnostics
            )

            print(
                "Sprint 3.6 Execution Diagnostics"
            )
            print(
                "-" * 60
            )
            print(
                report.summary
            )

            for line in report.lines:
                print(
                    line
                )

            if diagnostics.timeout_steps != (
                "system.health",
            ):
                raise RuntimeError(
                    "Timeout diagnostics are incorrect."
                )

            if diagnostics.retry_steps != (
                "system.ping",
                "system.health",
            ):
                raise RuntimeError(
                    "Retry diagnostics are incorrect."
                )

            print(
                "Execution diagnostics gate: PASS"
            )

        finally:
            await database.engine.dispose()


if __name__ == "__main__":
    asyncio.run(
        main()
    )
