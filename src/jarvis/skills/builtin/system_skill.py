from __future__ import annotations

from typing import Any

from jarvis.core.container import container
from jarvis.planner.execution_history import ExecutionHistoryService
from jarvis.planner.execution_history_report import (
    ExecutionHistoryReportBuilder,
)
from jarvis.planner.execution_persistence import (
    ExecutionPersistenceService,
)
from jarvis.services.capability import CapabilityDefinition
from jarvis.skills.base import Skill
from jarvis.skills.context import SkillContext
from jarvis.skills.metadata import SkillMetadata
from jarvis.version import __version__


class SystemSkill(Skill):
    _EXECUTION_HISTORY_LIMIT = 10

    def __init__(
        self,
        context: SkillContext,
    ) -> None:
        super().__init__()
        self.context = context

    @property
    def metadata(self) -> SkillMetadata:
        return SkillMetadata(
            name="system",
            version="1.1.0",
            description="Built-in system utilities",
            capabilities=[
                "system.ping",
                "system.health",
                "system.version",
                "system.execution_history",
            ],
            priority=1,
        )

    @property
    def capability_definitions(
        self,
    ) -> list[CapabilityDefinition]:
        return [
            CapabilityDefinition(
                name="system.ping",
                description=(
                    "Check whether JarvisAI is running "
                    "and responding."
                ),
            ),
            CapabilityDefinition(
                name="system.health",
                description=(
                    "Check the current health status "
                    "of JarvisAI."
                ),
            ),
            CapabilityDefinition(
                name="system.version",
                description=(
                    "Get the current JarvisAI version."
                ),
            ),
            CapabilityDefinition(
                name="system.execution_history",
                description=(
                    "Show recent JarvisAI planner execution "
                    "history. This is read-only."
                ),
            ),
        ]

    async def startup(self) -> None:
        pass

    async def shutdown(self) -> None:
        pass

    async def execute(
        self,
        command: str,
        **kwargs: Any,
    ) -> Any:
        del kwargs

        if command == "system.ping":
            return {
                "status": "ok",
            }

        if command == "system.version":
            return {
                "jarvis": __version__,
            }

        if command == "system.health":
            return await self.health()

        if command == "system.execution_history":
            return await self._execution_history()

        raise ValueError(
            f"Unsupported command: {command}"
        )

    async def health(self) -> dict[str, Any]:
        return {
            "healthy": True,
            "skill": self.metadata.name,
            "version": self.metadata.version,
        }

    async def _execution_history(
        self,
    ) -> dict[str, Any]:
        if not container.has(
            "execution_persistence"
        ):
            return {
                "available": False,
                "summary": (
                    "Execution history is not available."
                ),
                "records": [],
            }

        persistence = container.resolve(
            "execution_persistence",
            ExecutionPersistenceService,
        )

        history_service = ExecutionHistoryService(
            persistence
        )

        history = await history_service.recent(
            limit=self._EXECUTION_HISTORY_LIMIT
        )

        report = ExecutionHistoryReportBuilder().build(
            history
        )

        return {
            "available": True,
            "summary": report.summary,
            "records": list(
                report.lines
            ),
            "total": history.total,
            "completed": history.completed,
            "failed": history.failed,
        }
