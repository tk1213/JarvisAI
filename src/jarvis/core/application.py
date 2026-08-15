from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from jarvis.agent.bootstrap import register_ai_agent_runtime
from jarvis.agent.conversation_bridge import AIAgentConversationBridge
from jarvis.agent.memory_startup import AIAgentMemoryStartupService
from jarvis.agent.planning_context import AIAgentPlanningContextBuilder
from jarvis.ai.openai_client import OpenAIClient
from jarvis.config import settings
from jarvis.core.container import container
from jarvis.core.event_bus import event_bus
from jarvis.core.logger import log
from jarvis.core.plugin_loader import load_plugins
from jarvis.core.service_factory import ServiceFactory
from jarvis.core.task_manager import task_manager
from jarvis.database.db import DatabaseManager
from jarvis.memory.context import MemoryContextBuilder
from jarvis.memory.coordination import ConversationAgentMemoryCoordinator
from jarvis.planner.ai_generator import AIPlanGenerator
from jarvis.planner.conversation_bridge import PlannerConversationBridge
from jarvis.planner.execution_persistence import (
    ExecutionPersistenceService,
)
from jarvis.planner.execution_repository import (
    PlanExecutionRepository,
)
from jarvis.planner.orchestrator import PlannerOrchestrator
from jarvis.planner.persisting_executor import (
    PersistingPlanExecutor,
)
from jarvis.planner.resilience_runtime import (
    resilience_runtime,
)
from jarvis.planner.service import PlannerService
from jarvis.services.ai_capability_resolver import AICapabilityResolver
from jarvis.services.ai_service import AIService
from jarvis.services.capability_registry import CapabilityRegistry
from jarvis.services.capability_router import CapabilityRouter
from jarvis.services.command_service import CommandService
from jarvis.services.conversation_manager import ConversationManager
from jarvis.services.heartbeat_service import HeartbeatService
from jarvis.services.memory_service import MemoryService
from jarvis.services.system_service import SystemService
from jarvis.services.wake_word_service import WakeWordService
from jarvis.skills.context import SkillContext
from jarvis.skills.loader import SkillLoader
from jarvis.skills.manager import SkillManager
from jarvis.smart_home.service import SmartHomeService
from jarvis.tools.conversation_bridge import (
    ToolCallingConversationBridge,
)
from jarvis.tools.openai_runner import OpenAIToolCallingRunner
from jarvis.tools.safe import (
    ReadOnlyToolDefinitionFactory,
    ReadOnlyToolExecutor,
)


class JarvisApplication:
    def __init__(self) -> None:
        self.started = False

        self._system_started = False
        self._database_started = False
        self._smart_home_connected = False
        self._skills_started = False
        self._wake_word_created = False

    async def start(
        self,
        start_background_tasks: bool = True,
    ) -> None:
        if self.started:
            return

        log.info("Initializing Jarvis Application...")

        if len(container) > 0:
            container.clear()

        self._reset_lifecycle_state()

        try:
            factory = ServiceFactory(container)
            factory.register_all()

            self._wake_word_created = container.has(
                "wake_word"
            )

            system = container.resolve(
                "system",
                SystemService,
            )
            commands = container.resolve(
                "commands",
                CommandService,
            )
            database = container.resolve(
                "database",
                DatabaseManager,
            )
            smart_home_service = container.resolve(
                "smart_home",
                SmartHomeService,
            )
            heartbeat_service = container.resolve(
                "heartbeat",
                HeartbeatService,
            )
            ai_service = container.resolve(
                "ai",
                AIService,
            )
            memory_service = container.resolve(
                "memory",
                MemoryService,
            )
            conversation_manager = container.resolve(
                "conversation",
                ConversationManager,
            )

            skill_context = SkillContext(
                ai=ai_service,
                memory=memory_service,
                smart_home=smart_home_service,
                event_bus=event_bus,
                settings=settings,
            )

            skill_manager = SkillManager()

            skill_loader = SkillLoader(
                manager=skill_manager,
                context=skill_context,
            )

            skill_loader.load_package(
                "jarvis.skills.builtin",
            )

            capability_registry = (
                CapabilityRegistry.from_capabilities(
                    skill_manager.list_capability_definitions(),
                )
            )

            capability_router = CapabilityRouter(
                skill_manager=skill_manager,
                registry=capability_registry,
            )

            ai_capability_resolver = AICapabilityResolver(
                ai=ai_service,
                registry=capability_registry,
            )

            planner = PlannerService(
                capability_registry
            )

            execution_repository = PlanExecutionRepository(
                database
            )

            execution_persistence = ExecutionPersistenceService(
                execution_repository
            )

            plan_executor = PersistingPlanExecutor(
                capability_router,
                persistence=execution_persistence,
            )

            ai_plan_generator = AIPlanGenerator(
                ai=ai_service,
                registry=capability_registry,
                planner=planner,
            )

            planner_orchestrator = PlannerOrchestrator(
                generator=ai_plan_generator,
                planner=planner,
                executor=plan_executor,
            )

            planner_conversation = PlannerConversationBridge(
                planner_orchestrator
            )

            conversation_manager.set_planner_bridge(
                planner_conversation
            )

            if not isinstance(
                ai_service.client,
                OpenAIClient,
            ):
                raise TypeError(
                    "Native tool calling requires OpenAIClient."
                )

            tool_definitions = ReadOnlyToolDefinitionFactory(
                capability_registry
            )

            tool_executor = ReadOnlyToolExecutor(
                registry=capability_registry,
                router=capability_router,
            )

            openai_tool_runner = OpenAIToolCallingRunner(
                ai=ai_service.client,
                definitions=tool_definitions,
                executor=tool_executor,
            )

            tool_calling_conversation = (
                ToolCallingConversationBridge(
                    runner=openai_tool_runner,
                    fallback_ai=ai_service,
                )
            )

            conversation_manager.set_tool_calling_bridge(
                tool_calling_conversation
            )

            conversation_manager.set_capability_router(
                capability_router,
            )

            conversation_manager.set_capability_resolver(
                ai_capability_resolver,
            )

            container.register(
                "skill_manager",
                skill_manager,
                overwrite=False,
            )

            container.register(
                "capability_registry",
                capability_registry,
                overwrite=False,
            )

            container.register(
                "capability_router",
                capability_router,
                overwrite=False,
            )

            container.register(
                "ai_capability_resolver",
                ai_capability_resolver,
                overwrite=False,
            )

            container.register(
                "planner",
                planner,
                overwrite=False,
            )

            container.register(
                "plan_executor",
                plan_executor,
                overwrite=False,
            )

            container.register(
                "execution_repository",
                execution_repository,
                overwrite=False,
            )

            container.register(
                "execution_persistence",
                execution_persistence,
                overwrite=False,
            )

            container.register(
                "ai_plan_generator",
                ai_plan_generator,
                overwrite=False,
            )

            container.register(
                "planner_orchestrator",
                planner_orchestrator,
                overwrite=False,
            )

            register_ai_agent_runtime(
                container,
                overwrite=False,
            )

            if (
                container.has("memory_context")
                and container.has("ai_agent_planning_context")
            ):
                memory_coordinator = ConversationAgentMemoryCoordinator(
                    conversation_memory=container.resolve(
                        "memory_context",
                        MemoryContextBuilder,
                    ),
                    agent_memory=container.resolve(
                        "ai_agent_planning_context",
                        AIAgentPlanningContextBuilder,
                    ),
                )

                container.register(
                    "conversation_agent_memory_coordinator",
                    memory_coordinator,
                    overwrite=False,
                )

            ai_agent_runtime = container.get(
                "ai_agent_runtime"
            )

            ai_agent_conversation = (
                AIAgentConversationBridge(
                    ai_agent_runtime
                )
            )

            conversation_manager.set_ai_agent_bridge(
                ai_agent_conversation
            )

            container.register(
                "ai_agent_conversation",
                ai_agent_conversation,
                overwrite=False,
            )

            container.register(
                "resilience_runtime",
                resilience_runtime,
                overwrite=False,
            )

            container.register(
                "planner_conversation",
                planner_conversation,
                overwrite=False,
            )

            container.register(
                "tool_definitions",
                tool_definitions,
                overwrite=False,
            )

            container.register(
                "tool_executor",
                tool_executor,
                overwrite=False,
            )

            container.register(
                "openai_tool_runner",
                openai_tool_runner,
                overwrite=False,
            )

            container.register(
                "tool_calling_conversation",
                tool_calling_conversation,
                overwrite=False,
            )

            system.startup()
            self._system_started = True

            await database.startup()
            self._database_started = True

            if container.has(
                "ai_agent_memory_startup"
            ):
                agent_memory_startup = container.resolve(
                    "ai_agent_memory_startup",
                    AIAgentMemoryStartupService,
                )

                restored_records = await agent_memory_startup.restore()

                log.info(
                    "Restored {} durable agent memory record(s)",
                    restored_records,
                )

            try:
                await smart_home_service.connect()

            except Exception:  # noqa: BLE001
                log.exception(
                    "Smart Home connection failed; "
                    "continuing with Smart Home unavailable"
                )

            else:
                self._smart_home_connected = True

            await skill_manager.startup()
            self._skills_started = True

            commands.register_default_commands()

            if start_background_tasks:
                task_manager.create_task(
                    "heartbeat",
                    heartbeat_service.run(),
                )

            load_plugins()

            self.started = True
            log.info("Jarvis Application Ready")

        except Exception:
            log.exception(
                "Jarvis Application startup failed"
            )

            await self._rollback_startup()
            raise

    async def _rollback_startup(self) -> None:
        log.info(
            "Rolling back Jarvis Application startup..."
        )

        await self._safe_async_cleanup(
            "background tasks",
            task_manager.stop_all,
        )

        if self._skills_started:
            skill_manager = container.resolve(
                "skill_manager",
                SkillManager,
            )

            await self._safe_async_cleanup(
                "skills",
                skill_manager.shutdown,
            )

            self._skills_started = False

        if self._smart_home_connected:
            smart_home_service = container.resolve(
                "smart_home",
                SmartHomeService,
            )

            await self._safe_async_cleanup(
                "smart home",
                smart_home_service.disconnect,
            )

            self._smart_home_connected = False

        if self._database_started:
            database = container.resolve(
                "database",
                DatabaseManager,
            )

            await self._safe_async_cleanup(
                "database",
                database.shutdown,
            )

            self._database_started = False

        if self._system_started:
            system = container.resolve(
                "system",
                SystemService,
            )

            self._safe_sync_cleanup(
                "system",
                system.shutdown,
            )

            self._system_started = False

        if self._wake_word_created:
            wake_word = container.resolve(
                "wake_word",
                WakeWordService,
            )

            self._safe_sync_cleanup(
                "wake word",
                wake_word.close,
            )

            self._wake_word_created = False

        container.clear()
        self.started = False

        log.info(
            "Jarvis Application startup rollback complete"
        )

    async def shutdown(self) -> None:
        if (
            not self.started
            and not self._has_active_resources()
        ):
            return

        log.info("Shutting down Jarvis Application...")

        await self._safe_async_cleanup(
            "background tasks",
            task_manager.stop_all,
        )

        if self._skills_started:
            skill_manager = container.resolve(
                "skill_manager",
                SkillManager,
            )

            await self._safe_async_cleanup(
                "skills",
                skill_manager.shutdown,
            )

            self._skills_started = False

        if self._smart_home_connected:
            smart_home_service = container.resolve(
                "smart_home",
                SmartHomeService,
            )

            await self._safe_async_cleanup(
                "smart home",
                smart_home_service.disconnect,
            )

            self._smart_home_connected = False

        if self._database_started:
            database = container.resolve(
                "database",
                DatabaseManager,
            )

            await self._safe_async_cleanup(
                "database",
                database.shutdown,
            )

            self._database_started = False

        if self._system_started:
            system = container.resolve(
                "system",
                SystemService,
            )

            self._safe_sync_cleanup(
                "system",
                system.shutdown,
            )

            self._system_started = False

        if self._wake_word_created:
            wake_word = container.resolve(
                "wake_word",
                WakeWordService,
            )

            self._safe_sync_cleanup(
                "wake word",
                wake_word.close,
            )

            self._wake_word_created = False

        container.clear()
        self.started = False

        log.info("Jarvis Application Stopped")

    async def _safe_async_cleanup(
        self,
        name: str,
        cleanup: Callable[[], Awaitable[Any]],
    ) -> None:
        try:
            await cleanup()

        except Exception:  # noqa: BLE001
            log.exception(
                "Cleanup failed: {}",
                name,
            )

    def _safe_sync_cleanup(
        self,
        name: str,
        cleanup: Callable[[], Any],
    ) -> None:
        try:
            cleanup()

        except Exception:  # noqa: BLE001
            log.exception(
                "Cleanup failed: {}",
                name,
            )

    def _has_active_resources(self) -> bool:
        return any(
            (
                self._system_started,
                self._database_started,
                self._smart_home_connected,
                self._skills_started,
                self._wake_word_created,
            )
        )

    def _reset_lifecycle_state(self) -> None:
        self.started = False

        self._system_started = False
        self._database_started = False
        self._smart_home_connected = False
        self._skills_started = False
        self._wake_word_created = False