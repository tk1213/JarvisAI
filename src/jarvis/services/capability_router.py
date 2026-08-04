from __future__ import annotations

from typing import Any

from jarvis.services.capability import CapabilityRequest
from jarvis.services.capability_registry import CapabilityRegistry
from jarvis.skills.manager import SkillManager


class CapabilityRouter:
    def __init__(
        self,
        skill_manager: SkillManager,
        registry: CapabilityRegistry | None = None,
    ) -> None:
        self._skill_manager = skill_manager
        self._registry = registry

    async def execute(
        self,
        capability: str,
        **kwargs: Any,
    ) -> Any:
        """
        Execute a capability using the registered Skill.

        Kept for backward compatibility.
        """
        request = CapabilityRequest(
            capability=capability,
            arguments=kwargs,
        )

        return await self.execute_request(request)

    async def execute_request(
        self,
        request: CapabilityRequest,
    ) -> Any:
        """
        Execute a structured capability request.
        """

        if (
            self._registry is not None
            and not self._registry.is_allowed(
                request.capability
            )
        ):
            raise PermissionError(
                "Capability is not allowed: "
                f"{request.capability}"
            )

        return await self._skill_manager.execute(
            request.capability,
            **request.arguments,
        )