from __future__ import annotations

import asyncio
from typing import Any

from loguru import logger

from jarvis.services.capability import CapabilityDefinition
from jarvis.skills.base import Skill
from jarvis.skills.registry import SkillRegistry
from jarvis.skills.resolver import SkillResolver


class SkillManager:
    def __init__(self) -> None:
        self._registry = SkillRegistry()
        self._resolver = SkillResolver(self._registry)

        self._started_skills: set[str] = set()
        self._startup_errors: dict[str, str] = {}

    @property
    def registry(self) -> SkillRegistry:
        return self._registry

    @property
    def resolver(self) -> SkillResolver:
        return self._resolver

    @property
    def is_degraded(self) -> bool:
        return bool(self._startup_errors)

    def register(
        self,
        skill: Skill,
        *,
        overwrite: bool = False,
    ) -> None:
        self._registry.register(
            skill,
            overwrite=overwrite,
        )

        logger.info(
            "Registered skill: {} ({})",
            skill.metadata.name,
            skill.metadata.version,
        )

    def list_capabilities(self) -> list[str]:
        capabilities = {
            capability
            for skill in self._registry
            if skill.enabled and skill.metadata.enabled
            for capability in skill.metadata.capabilities
        }

        return sorted(capabilities)

    def list_capability_definitions(
        self,
    ) -> list[CapabilityDefinition]:
        definitions: dict[str, CapabilityDefinition] = {}

        for skill in self._registry:
            if not skill.enabled:
                continue

            if not skill.metadata.enabled:
                continue

            for definition in skill.capability_definitions:
                definitions[definition.name] = definition

        return [
            definitions[name]
            for name in sorted(definitions)
        ]

    def list_started_skills(self) -> list[str]:
        return sorted(self._started_skills)

    def startup_errors(self) -> dict[str, str]:
        return dict(self._startup_errors)

    async def startup(self) -> None:
        self._started_skills.clear()
        self._startup_errors.clear()

        for skill in self._registry:
            if not skill.enabled:
                continue

            if not skill.metadata.enabled:
                continue

            skill_name = skill.metadata.name

            logger.info(
                "Starting skill: {}",
                skill_name,
            )

            try:
                await skill.startup()

            except Exception as exc:  # noqa: BLE001
                skill.enabled = False

                self._startup_errors[
                    skill_name
                ] = str(exc)

                logger.exception(
                    "Skill startup failed: {}",
                    skill_name,
                )

                continue

            self._started_skills.add(
                skill_name
            )

        if self._startup_errors:
            logger.warning(
                "Skill system started in degraded mode. "
                "Failed skills: {}",
                ", ".join(
                    sorted(self._startup_errors)
                ),
            )

    async def shutdown(self) -> None:
        cancellation: asyncio.CancelledError | None = None

        for skill in reversed(
            list(self._registry)
        ):
            skill_name = skill.metadata.name

            if skill_name not in self._started_skills:
                continue

            logger.info(
                "Stopping skill: {}",
                skill_name,
            )

            try:
                await skill.shutdown()

            except asyncio.CancelledError as exc:
                if cancellation is None:
                    cancellation = exc

            except Exception:  # noqa: BLE001
                logger.exception(
                    "Skill shutdown failed: {}",
                    skill_name,
                )

            finally:
                self._started_skills.discard(
                    skill_name
                )

        if cancellation is not None:
            raise cancellation

    async def health(self) -> dict[str, dict[str, Any]]:
        result: dict[str, dict[str, Any]] = {}

        for skill in self._registry:
            skill_name = skill.metadata.name

            startup_error = self._startup_errors.get(
                skill_name
            )

            if startup_error is not None:
                result[skill_name] = {
                    "healthy": False,
                    "enabled": False,
                    "error": startup_error,
                }
                continue

            try:
                health = await skill.health()

            except Exception as exc:  # noqa: BLE001
                logger.exception(
                    "Skill health check failed: {}",
                    skill_name,
                )

                result[skill_name] = {
                    "healthy": False,
                    "enabled": skill.enabled,
                    "error": str(exc),
                }
                continue

            result[skill_name] = health

        return result

    async def execute(
        self,
        capability: str,
        **kwargs: Any,
    ) -> Any:
        skill = self._resolver.resolve(capability)

        if skill is None:
            raise LookupError(
                f"No skill supports capability '{capability}'."
            )

        if not skill.enabled:
            raise RuntimeError(
                f"Skill '{skill.metadata.name}' is disabled."
            )

        return await skill.execute(
            capability,
            **kwargs,
        )