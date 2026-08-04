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
from jarvis.planner.execution_persistence import (
    ExecutionPersistenceService,
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
            / "execution_persistence.db"
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

            service = ExecutionPersistenceService(
                repository
            )

            await service.startup()

            executor = PlanExecutor(
                router=DemoRouter(),  # type: ignore[arg-type]
            )

            plan = Plan(
                goal="Persist execution through service",
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

            record_id = await service.persist_execution(
                execution
            )

            loaded = await service.get(
                record_id
            )

            recent = await service.list_recent(
                limit=10
            )

            if loaded is None:
                raise RuntimeError(
                    "Persisted record could not be loaded."
                )

            print(
                "Sprint 3.5 Execution Persistence Service"
            )
            print(
                "-" * 60
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
                f"Recent records: {len(recent)}"
            )

            if loaded.goal != plan.goal:
                raise RuntimeError(
                    "Persisted record goal mismatch."
                )

            if len(recent) != 1:
                raise RuntimeError(
                    "Recent execution history mismatch."
                )

            print(
                "Execution persistence service gate: PASS"
            )

        finally:
            await database.engine.dispose()


if __name__ == "__main__":
    asyncio.run(
        main()
    )
