from __future__ import annotations

import asyncio
import tempfile
from pathlib import Path
from typing import Any

from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
)

from jarvis.database.db import DatabaseManager
from jarvis.planner.execution_record import (
    PlanExecutionRecordBuilder,
)
from jarvis.planner.execution_repository import (
    PlanExecutionRepository,
)
from jarvis.planner.executor import PlanExecutor
from jarvis.planner.models import (
    Plan,
    PlanStatus,
    PlanStep,
)


class DemoRouter:
    async def execute_request(
        self,
        request,
    ) -> Any:
        return {
            "capability": request.capability,
            "status": "ok",
        }


async def main() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = (
            Path(temp_dir)
            / "execution_records.db"
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

            await repository.startup()

            executor = PlanExecutor(
                router=DemoRouter(),  # type: ignore[arg-type]
            )

            plan = Plan(
                goal="Persist execution record",
                steps=[
                    PlanStep(
                        index=1,
                        capability="system.ping",
                    )
                ],
                status=PlanStatus.READY,
            )

            execution = await executor.execute(
                plan
            )

            record = (
                PlanExecutionRecordBuilder()
                .build(
                    execution
                )
            )

            record_id = await repository.save(
                record
            )

            loaded = await repository.get(
                record_id
            )

            if loaded is None:
                raise RuntimeError(
                    "Execution record was not loaded."
                )

            recent = await repository.list_recent(
                limit=5
            )

            print(
                "Sprint 3.5 Execution Repository"
            )
            print(
                "-" * 60
            )
            print(
                f"Temporary DB: {db_path.name}"
            )
            print(
                f"Record ID: {record_id}"
            )
            print(
                f"Goal: {loaded.goal}"
            )
            print(
                f"Status: {loaded.plan_status}"
            )
            print(
                f"Steps: {len(loaded.steps)}"
            )
            print(
                f"Events: {len(loaded.events)}"
            )
            print(
                f"Recent records: {len(recent)}"
            )

            if loaded.goal != record.goal:
                raise RuntimeError(
                    "Loaded execution record does not match."
                )

            if len(recent) != 1:
                raise RuntimeError(
                    "Recent execution record query failed."
                )

            print(
                "Execution repository gate: PASS"
            )

        finally:
            await database.engine.dispose()


if __name__ == "__main__":
    asyncio.run(
        main()
    )
