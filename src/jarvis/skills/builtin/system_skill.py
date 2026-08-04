from __future__ import annotations

from typing import Any

from jarvis.core.container import container
from jarvis.planner.capability_reliability import (
    CapabilityReliabilityService,
)
from jarvis.planner.capability_reliability_report import (
    CapabilityReliabilityReportBuilder,
)
from jarvis.planner.execution_detail import ExecutionDetailService
from jarvis.planner.execution_detail_report import (
    ExecutionDetailReportBuilder,
)
from jarvis.planner.execution_diagnostics import (
    ExecutionDiagnosticsService,
)
from jarvis.planner.execution_diagnostics_report import (
    ExecutionDiagnosticsReportBuilder,
)
from jarvis.planner.execution_health import ExecutionHealthService
from jarvis.planner.execution_health_report import (
    ExecutionHealthReportBuilder,
)
from jarvis.planner.execution_health_trend_report import (
    ExecutionHealthTrendReportBuilder,
)
from jarvis.planner.execution_health_trends import (
    ExecutionHealthTrendService,
)
from jarvis.planner.execution_history import ExecutionHistoryService
from jarvis.planner.execution_history_report import (
    ExecutionHistoryReportBuilder,
)
from jarvis.planner.execution_persistence import (
    ExecutionPersistenceService,
)
from jarvis.planner.execution_statistics import (
    ExecutionStatisticsService,
)
from jarvis.planner.execution_statistics_report import (
    ExecutionStatisticsReportBuilder,
)
from jarvis.services.capability import CapabilityDefinition
from jarvis.skills.base import Skill
from jarvis.skills.context import SkillContext
from jarvis.skills.metadata import SkillMetadata
from jarvis.version import __version__


class SystemSkill(Skill):
    _EXECUTION_HISTORY_LIMIT = 10
    _EXECUTION_OBSERVABILITY_LIMIT = 100
    _EXECUTION_TREND_WINDOW_SIZE = 20

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
            version="1.3.0",
            description="Built-in system utilities",
            capabilities=[
                "system.ping",
                "system.health",
                "system.version",
                "system.execution_history",
                "system.execution_detail",
                "system.execution_diagnostics",
                "system.execution_statistics",
                "system.capability_reliability",
                "system.execution_health",
                "system.execution_health_trend",
            ],
            priority=1,
        )

    @property
    def capability_definitions(
        self,
    ) -> list[CapabilityDefinition]:
        record_id_argument = {
            "record_id": (
                "Execution record ID as a positive integer."
            ),
        }

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
            CapabilityDefinition(
                name="system.execution_detail",
                description=(
                    "Show detailed information for one "
                    "persisted planner execution. Read-only."
                ),
                arguments=record_id_argument,
            ),
            CapabilityDefinition(
                name="system.execution_diagnostics",
                description=(
                    "Diagnose failures, retries, and timeouts "
                    "for one persisted planner execution. "
                    "Read-only."
                ),
                arguments=record_id_argument,
            ),
            CapabilityDefinition(
                name="system.execution_statistics",
                description=(
                    "Summarize recent planner execution "
                    "statistics. Read-only."
                ),
            ),
            CapabilityDefinition(
                name="system.capability_reliability",
                description=(
                    "Summarize recent reliability metrics "
                    "for planner capabilities. Read-only."
                ),
            ),
            CapabilityDefinition(
                name="system.execution_health",
                description=(
                    "Show advisory execution health based on "
                    "recent persisted planner history. Read-only."
                ),
            ),
            CapabilityDefinition(
                name="system.execution_health_trend",
                description=(
                    "Show the recent execution health trend "
                    "using persisted planner history. Read-only."
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

        if command == "system.execution_detail":
            return await self._execution_detail(
                self._record_id_from_kwargs(
                    kwargs
                )
            )

        if command == "system.execution_diagnostics":
            return await self._execution_diagnostics(
                self._record_id_from_kwargs(
                    kwargs
                )
            )

        if command == "system.execution_statistics":
            return await self._execution_statistics()

        if command == "system.capability_reliability":
            return await self._capability_reliability()

        if command == "system.execution_health":
            return await self._execution_health()

        if command == "system.execution_health_trend":
            return await self._execution_health_trend()

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
        persistence = self._resolve_persistence()

        if persistence is None:
            return {
                "available": False,
                "summary": (
                    "Execution history is not available."
                ),
                "records": [],
            }

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

    async def _execution_detail(
        self,
        record_id: int,
    ) -> dict[str, Any]:
        persistence = self._resolve_persistence()

        if persistence is None:
            return {
                "available": False,
                "record_id": record_id,
                "summary": (
                    "Execution detail is not available."
                ),
                "steps": [],
                "timeline": [],
            }

        detail_service = ExecutionDetailService(
            persistence
        )

        detail = await detail_service.get(
            record_id
        )

        if detail is None:
            return {
                "available": False,
                "record_id": record_id,
                "summary": (
                    f"Execution record {record_id} was not found."
                ),
                "steps": [],
                "timeline": [],
            }

        report = ExecutionDetailReportBuilder().build(
            detail
        )

        return {
            "available": True,
            "record_id": detail.record_id,
            "summary": report.summary,
            "steps": list(
                report.step_lines
            ),
            "timeline": list(
                report.timeline_lines
            ),
            "status": detail.plan_status,
            "success": detail.success,
            "completed_steps": detail.completed_steps,
            "failure_count": detail.failure_count,
        }

    async def _execution_diagnostics(
        self,
        record_id: int,
    ) -> dict[str, Any]:
        persistence = self._resolve_persistence()

        if persistence is None:
            return {
                "available": False,
                "record_id": record_id,
                "summary": (
                    "Execution diagnostics are not available."
                ),
                "findings": [],
            }

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
            return {
                "available": False,
                "record_id": record_id,
                "summary": (
                    f"Execution record {record_id} was not found."
                ),
                "findings": [],
            }

        report = ExecutionDiagnosticsReportBuilder().build(
            diagnostics
        )

        return {
            "available": True,
            "record_id": diagnostics.record_id,
            "summary": report.summary,
            "findings": list(
                report.lines
            ),
            "failed_steps": list(
                diagnostics.failed_steps
            ),
            "retry_steps": list(
                diagnostics.retry_steps
            ),
            "timeout_steps": list(
                diagnostics.timeout_steps
            ),
        }

    async def _execution_statistics(
        self,
    ) -> dict[str, Any]:
        persistence = self._resolve_persistence()

        if persistence is None:
            return self._unavailable_summary(
                "Execution statistics are not available."
            )

        service = ExecutionStatisticsService(
            persistence
        )
        statistics = await service.summarize(
            limit=self._EXECUTION_OBSERVABILITY_LIMIT
        )
        report = ExecutionStatisticsReportBuilder().build(
            statistics
        )

        return {
            "available": True,
            "summary": report.summary,
            "lines": list(
                report.lines
            ),
            "total": statistics.total,
            "completed": statistics.completed,
            "failed": statistics.failed,
            "success_rate": statistics.success_rate,
            "retried_steps": statistics.retried_steps,
            "timed_out_steps": statistics.timed_out_steps,
        }

    async def _capability_reliability(
        self,
    ) -> dict[str, Any]:
        persistence = self._resolve_persistence()

        if persistence is None:
            return self._unavailable_summary(
                "Capability reliability is not available."
            )

        service = CapabilityReliabilityService(
            persistence
        )
        reliability = await service.summarize(
            limit=self._EXECUTION_OBSERVABILITY_LIMIT
        )
        report = CapabilityReliabilityReportBuilder().build(
            reliability
        )

        return {
            "available": True,
            "summary": report.summary,
            "lines": list(
                report.lines
            ),
            "total_capabilities": (
                reliability.total_capabilities
            ),
        }

    async def _execution_health(
        self,
    ) -> dict[str, Any]:
        persistence = self._resolve_persistence()

        if persistence is None:
            return self._unavailable_summary(
                "Execution health is not available."
            )

        statistics = ExecutionStatisticsService(
            persistence
        )
        reliability = CapabilityReliabilityService(
            persistence
        )
        health_service = ExecutionHealthService(
            statistics,
            reliability,
        )

        snapshot = await health_service.check(
            limit=self._EXECUTION_OBSERVABILITY_LIMIT
        )
        report = ExecutionHealthReportBuilder().build(
            snapshot
        )

        return {
            "available": True,
            "summary": report.summary,
            "lines": list(
                report.lines
            ),
            "level": snapshot.level.value,
            "total_executions": snapshot.total_executions,
            "success_rate": snapshot.success_rate,
            "retried_steps": snapshot.retried_steps,
            "timed_out_steps": snapshot.timed_out_steps,
            "unreliable_capabilities": list(
                snapshot.unreliable_capabilities
            ),
        }

    async def _execution_health_trend(
        self,
    ) -> dict[str, Any]:
        persistence = self._resolve_persistence()

        if persistence is None:
            return self._unavailable_summary(
                "Execution health trend is not available."
            )

        service = ExecutionHealthTrendService(
            persistence
        )
        trend = await service.summarize(
            window_size=self._EXECUTION_TREND_WINDOW_SIZE
        )
        report = ExecutionHealthTrendReportBuilder().build(
            trend
        )

        return {
            "available": True,
            "summary": report.summary,
            "lines": list(
                report.lines
            ),
            "direction": trend.direction,
            "level": trend.level.value,
            "current_size": trend.current.size,
            "previous_size": trend.previous.size,
            "current_success_rate": (
                trend.current.success_rate
            ),
            "previous_success_rate": (
                trend.previous.success_rate
            ),
        }

    @staticmethod
    def _unavailable_summary(
        message: str,
    ) -> dict[str, Any]:
        return {
            "available": False,
            "summary": message,
            "lines": [],
        }

    @staticmethod
    def _record_id_from_kwargs(
        kwargs: dict[str, Any],
    ) -> int:
        raw_value = kwargs.get(
            "record_id"
        )

        if raw_value is None:
            raise ValueError(
                "record_id is required."
            )

        try:
            record_id = int(
                str(raw_value).strip()
            )
        except ValueError as exc:
            raise ValueError(
                "record_id must be a positive integer."
            ) from exc

        if record_id < 1:
            raise ValueError(
                "record_id must be a positive integer."
            )

        return record_id

    @staticmethod
    def _resolve_persistence(
    ) -> ExecutionPersistenceService | None:
        if not container.has(
            "execution_persistence"
        ):
            return None

        return container.resolve(
            "execution_persistence",
            ExecutionPersistenceService,
        )
