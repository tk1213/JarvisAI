from __future__ import annotations

from jarvis.agent.memory import AIAgentMemoryLifecycle
from jarvis.agent.memory_persistence import AIAgentMemoryPersistence
from jarvis.agent.memory_repository import AIAgentMemoryRepository
from jarvis.agent.memory_retention import AIAgentMemoryRetentionPolicy
from jarvis.agent.memory_startup import AIAgentMemoryStartupService
from jarvis.agent.planning_context import AIAgentPlanningContextBuilder
from jarvis.agent.replanning import AIAgentReplanPolicy
from jarvis.agent.runtime import AIAgentRuntime
from jarvis.agent.session import AIAgentSessionService
from jarvis.core.container import ServiceContainer
from jarvis.database.db import DatabaseManager
from jarvis.planner.ai_plan_memory import AIPlanMemoryStore
from jarvis.planner.ai_plan_reflection import AIPlanReflectionService
from jarvis.planner.orchestrator import PlannerOrchestrator


def register_ai_agent_runtime(
    container: ServiceContainer,
    *,
    overwrite: bool = False,
) -> AIAgentRuntime:
    orchestrator = container.resolve(
        "planner_orchestrator",
        PlannerOrchestrator,
    )

    memory = AIPlanMemoryStore()

    memory_repository: AIAgentMemoryRepository | None = None
    memory_persistence: AIAgentMemoryPersistence | None = None
    memory_retention: AIAgentMemoryRetentionPolicy | None = None

    if container.has(
        "database"
    ):
        database = container.resolve(
            "database",
            DatabaseManager,
        )

        memory_repository = AIAgentMemoryRepository(
            database
        )
        memory_retention = AIAgentMemoryRetentionPolicy(
            memory_repository,
            max_records=500,
        )
        memory_persistence = AIAgentMemoryPersistence(
            repository=memory_repository,
            store=memory,
            retention=memory_retention,
        )

    memory_lifecycle = AIAgentMemoryLifecycle(
        memory,
        persistence=memory_persistence,
    )
    planning_context = AIAgentPlanningContextBuilder(
        memory_lifecycle
    )
    replan_policy = AIAgentReplanPolicy()

    runtime = AIAgentRuntime(
        orchestrator=orchestrator,
        reflection=AIPlanReflectionService(),
        memory=memory,
        memory_lifecycle=memory_lifecycle,
        planning_context=planning_context,
        replan_policy=replan_policy,
    )

    container.register(
        "ai_plan_memory",
        memory,
        overwrite=overwrite,
    )

    if memory_repository is not None:
        container.register(
            "ai_agent_memory_repository",
            memory_repository,
            overwrite=overwrite,
        )

    if memory_persistence is not None:
        container.register(
            "ai_agent_memory_persistence",
            memory_persistence,
            overwrite=overwrite,
        )

        if memory_retention is None:
            raise RuntimeError(
                "Agent memory retention policy was not created."
            )

        container.register(
            "ai_agent_memory_retention",
            memory_retention,
            overwrite=overwrite,
        )

        container.register(
            "ai_agent_memory_startup",
            AIAgentMemoryStartupService(
                memory_lifecycle,
                retention=memory_retention,
            ),
            overwrite=overwrite,
        )

    container.register(
        "ai_agent_memory_lifecycle",
        memory_lifecycle,
        overwrite=overwrite,
    )

    container.register(
        "ai_agent_planning_context",
        planning_context,
        overwrite=overwrite,
    )

    container.register(
        "ai_agent_replan_policy",
        replan_policy,
        overwrite=overwrite,
    )

    session = AIAgentSessionService(
        runtime=runtime,
        memory=memory,
        memory_lifecycle=memory_lifecycle,
    )

    container.register(
        "ai_agent_session",
        session,
        overwrite=overwrite,
    )

    container.register(
        "ai_agent_runtime",
        runtime,
        overwrite=overwrite,
    )

    return runtime
