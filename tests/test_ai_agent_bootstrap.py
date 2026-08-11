from __future__ import annotations

from unittest.mock import Mock

from jarvis.agent.bootstrap import register_ai_agent_runtime
from jarvis.agent.runtime import AIAgentRuntime
from jarvis.core.container import ServiceContainer
from jarvis.planner.ai_plan_memory import AIPlanMemoryStore
from jarvis.planner.orchestrator import PlannerOrchestrator


def test_bootstrap_registers_agent_runtime_and_memory() -> None:
    container = ServiceContainer()

    orchestrator = Mock(
        spec=PlannerOrchestrator
    )

    container.register(
        "planner_orchestrator",
        orchestrator,
    )

    runtime = register_ai_agent_runtime(
        container
    )

    assert isinstance(
        runtime,
        AIAgentRuntime,
    )

    assert container.resolve(
        "ai_agent_runtime",
        AIAgentRuntime,
    ) is runtime

    assert isinstance(
        container.resolve(
            "ai_plan_memory",
            AIPlanMemoryStore,
        ),
        AIPlanMemoryStore,
    )


def test_bootstrap_rejects_duplicate_registration() -> None:
    container = ServiceContainer()

    container.register(
        "planner_orchestrator",
        Mock(
            spec=PlannerOrchestrator
        ),
    )

    register_ai_agent_runtime(
        container
    )

    try:
        register_ai_agent_runtime(
            container
        )
    except ValueError as exc:
        assert (
            "already registered"
            in str(
                exc
            )
        )
    else:
        raise AssertionError(
            "Expected duplicate registration to fail."
        )



def test_bootstrap_registers_agent_memory_lifecycle() -> None:
    from jarvis.agent.memory import AIAgentMemoryLifecycle

    container = ServiceContainer()

    container.register(
        "planner_orchestrator",
        Mock(
            spec=PlannerOrchestrator
        ),
    )

    runtime = register_ai_agent_runtime(
        container
    )

    lifecycle = container.resolve(
        "ai_agent_memory_lifecycle",
        AIAgentMemoryLifecycle,
    )

    assert lifecycle is runtime.memory_lifecycle
    assert lifecycle.store is container.resolve(
        "ai_plan_memory",
        AIPlanMemoryStore,
    )



def test_bootstrap_registers_agent_planning_context() -> None:
    from jarvis.agent.planning_context import AIAgentPlanningContextBuilder

    container = ServiceContainer()

    container.register(
        "planner_orchestrator",
        Mock(
            spec=PlannerOrchestrator
        ),
    )

    register_ai_agent_runtime(
        container
    )

    assert isinstance(
        container.resolve(
            "ai_agent_planning_context",
            AIAgentPlanningContextBuilder,
        ),
        AIAgentPlanningContextBuilder,
    )



def test_bootstrap_registers_agent_replan_policy() -> None:
    from jarvis.agent.replanning import AIAgentReplanPolicy

    container = ServiceContainer()

    container.register(
        "planner_orchestrator",
        Mock(
            spec=PlannerOrchestrator
        ),
    )

    register_ai_agent_runtime(
        container
    )

    assert isinstance(
        container.resolve(
            "ai_agent_replan_policy",
            AIAgentReplanPolicy,
        ),
        AIAgentReplanPolicy,
    )



def test_bootstrap_registers_agent_session_service() -> None:
    from jarvis.agent.session import AIAgentSessionService

    container = ServiceContainer()

    container.register(
        "planner_orchestrator",
        Mock(
            spec=PlannerOrchestrator
        ),
    )

    register_ai_agent_runtime(
        container
    )

    assert isinstance(
        container.resolve(
            "ai_agent_session",
            AIAgentSessionService,
        ),
        AIAgentSessionService,
    )



def test_bootstrap_registers_durable_memory_services_when_database_exists() -> None:
    from jarvis.agent.memory_persistence import AIAgentMemoryPersistence
    from jarvis.agent.memory_repository import AIAgentMemoryRepository
    from jarvis.database.db import DatabaseManager

    container = ServiceContainer()

    container.register(
        "planner_orchestrator",
        Mock(
            spec=PlannerOrchestrator
        ),
    )
    container.register(
        "database",
        Mock(
            spec=DatabaseManager
        ),
    )

    register_ai_agent_runtime(
        container
    )

    assert isinstance(
        container.resolve(
            "ai_agent_memory_repository",
            AIAgentMemoryRepository,
        ),
        AIAgentMemoryRepository,
    )
    assert isinstance(
        container.resolve(
            "ai_agent_memory_persistence",
            AIAgentMemoryPersistence,
        ),
        AIAgentMemoryPersistence,
    )



def test_bootstrap_registers_agent_memory_startup_service() -> None:
    from jarvis.agent.memory_startup import AIAgentMemoryStartupService
    from jarvis.database.db import DatabaseManager

    container = ServiceContainer()

    container.register(
        "planner_orchestrator",
        Mock(
            spec=PlannerOrchestrator
        ),
    )
    container.register(
        "database",
        Mock(
            spec=DatabaseManager
        ),
    )

    register_ai_agent_runtime(
        container
    )

    assert isinstance(
        container.resolve(
            "ai_agent_memory_startup",
            AIAgentMemoryStartupService,
        ),
        AIAgentMemoryStartupService,
    )



def test_bootstrap_registers_agent_memory_retention_policy() -> None:
    from jarvis.agent.memory_retention import AIAgentMemoryRetentionPolicy
    from jarvis.database.db import DatabaseManager

    container = ServiceContainer()

    container.register(
        "planner_orchestrator",
        Mock(
            spec=PlannerOrchestrator
        ),
    )
    container.register(
        "database",
        Mock(
            spec=DatabaseManager
        ),
    )

    register_ai_agent_runtime(
        container
    )

    retention = container.resolve(
        "ai_agent_memory_retention",
        AIAgentMemoryRetentionPolicy,
    )

    assert retention.max_records == 500
