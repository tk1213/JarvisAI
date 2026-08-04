from __future__ import annotations

import json
from typing import Any

from jarvis.services.ai_service import AIService
from jarvis.services.capability import (
    CapabilityDefinition,
    CapabilityRequest,
)
from jarvis.services.capability_registry import CapabilityRegistry


class AICapabilityResolver:
    def __init__(
        self,
        ai: AIService,
        registry: CapabilityRegistry,
    ) -> None:
        self._ai = ai
        self._registry = registry

    async def resolve(
        self,
        text: str,
    ) -> CapabilityRequest | None:
        text = text.strip()

        if not text:
            return None

        definitions = self._registry.list_definitions()

        if not definitions:
            return None

        prompt = self._build_prompt(
            text=text,
            definitions=definitions,
        )

        response = await self._ai.ask(prompt)

        data = self._parse_response(response)

        if data is None:
            return None

        capability = data.get("capability")

        if not isinstance(capability, str):
            return None

        capability = capability.strip()

        if not self._registry.is_allowed(capability):
            return None

        arguments = data.get(
            "arguments",
            {},
        )

        if not isinstance(arguments, dict):
            return None

        return CapabilityRequest(
            capability=capability,
            arguments=arguments,
        )

    @staticmethod
    def _build_prompt(
        *,
        text: str,
        definitions: list[CapabilityDefinition],
    ) -> str:
        capability_sections = [
            AICapabilityResolver._format_definition(
                definition
            )
            for definition in definitions
        ]

        capability_text = "\n\n".join(
            capability_sections
        )

        return (
            "You are a capability resolver for JarvisAI.\n"
            "Determine whether the user's request matches one of the "
            "allowed capabilities.\n\n"
            "Allowed capabilities:\n"
            f"{capability_text}\n\n"
            "Rules:\n"
            "- Select only one capability from the list above.\n"
            "- Never invent a capability.\n"
            "- Only include arguments relevant to the selected "
            "capability.\n"
            "- If no capability clearly matches, return null.\n"
            "- Return JSON only.\n\n"
            "If a capability matches, return:\n"
            '{"capability":"capability.name","arguments":{}}\n\n'
            "If none match, return:\n"
            '{"capability":null,"arguments":{}}\n\n'
            f"User request:\n{text}"
        )

    @staticmethod
    def _format_definition(
        definition: CapabilityDefinition,
    ) -> str:
        lines = [
            f"Name: {definition.name}",
        ]

        if definition.description:
            lines.append(
                f"Description: {definition.description}"
            )

        if definition.arguments:
            lines.append("Arguments:")

            for name, description in sorted(
                definition.arguments.items()
            ):
                lines.append(
                    f"- {name}: {description}"
                )
        else:
            lines.append("Arguments: none")

        return "\n".join(lines)

    @staticmethod
    def _parse_response(
        response: str,
    ) -> dict[str, Any] | None:
        response = response.strip()

        if not response:
            return None

        if response.startswith("```"):
            lines = response.splitlines()

            if lines:
                lines = lines[1:]

            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]

            response = "\n".join(lines).strip()

        try:
            data = json.loads(response)
        except json.JSONDecodeError:
            return None

        if not isinstance(data, dict):
            return None

        return data