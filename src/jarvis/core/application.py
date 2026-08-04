from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from jarvis.config import settings
from jarvis.core.container import container
from jarvis.core.event_bus import event_bus
from jarvis.core.logger import log
from jarvis.core.plugin_loader import load_plugins
from jarvis.core.service_factory import ServiceFactory
from jarvis.core.task_manager import task_manager
from jarvis.database.db import DatabaseManager
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

            self._wake_word_created = True

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

            system.startup()
            self._system_started = True

            await database.startup()
            self._database_started = True

            await smart_home_service.connect()
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