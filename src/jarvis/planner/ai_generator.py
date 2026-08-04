from __future__ import annotations

import json
from typing import Any

from jarvis.planner.models import Plan
from jarvis.planner.service import PlannerService
from jarvis.services.ai_service import AIService
from jarvis.services.capability import CapabilityRequest
from jarvis.services.capability_registry import CapabilityRegistry


class AIPlanGenerator:
    def __init__(
        self,
        *,
        ai: AIService,
        registry: CapabilityRegistry,
        planner: PlannerService,
        max_steps: int = 8,
    ) -> None:
        if max_steps < 1:
            raise ValueError(
                "max_steps must be at least 1."
            )

        self._ai = ai
        self._registry = registry
        self._planner = planner
        self._max_steps = max_steps

    async def generate(
        self,
        text: str,
    ) -> Plan | None:
        text = text.strip()

        if not text:
            return None

        definitions = (
            self._registry.list_definitions()
        )

        if not definitions:
            return None

        prompt = self._build_prompt(
            text=text,
            definitions=definitions,
        )

        response = await self._ai.ask(
            prompt
        )

        data = self._parse_response(
            response
        )

        if data is None:
            return None

        requests = self._parse_requests(
            data
        )

        if not requests:
            return None

        if len(requests) > self._max_steps:
            raise ValueError(
                "Generated plan exceeds maximum step count."
            )

        return self._planner.create_plan(
            goal=text,
            requests=requests,
        )

    def _parse_requests(
        self,
        data: dict[str, Any],
    ) -> list[CapabilityRequest]:
        raw_steps = data.get(
            "steps"
        )

        if not isinstance(
            raw_steps,
            list,
        ):
            return []

        requests: list[CapabilityRequest] = []

        for raw_step in raw_steps:
            if not isinstance(
                raw_step,
                dict,
            ):
                return []

            capability = raw_step.get(
                "capability"
            )

            if not isinstance(
                capability,
                str,
            ):
                return []

            capability = capability.strip()

            if not capability:
                return []

            if not self._registry.is_allowed(
                capability
            ):
                raise PermissionError(
                    "Capability is not allowed: "
                    f"{capability}"
                )

            arguments = raw_step.get(
                "arguments",
                {},
            )

            if not isinstance(
                arguments,
                dict,
            ):
                return []

            requests.append(
                CapabilityRequest(
                    capability=capability,
                    arguments=arguments,
                )
            )

        return requests

    @staticmethod
    def _build_prompt(
        *,
        text: str,
        definitions: list[Any],
    ) -> str:
        sections: list[str] = []

        for definition in definitions:
            lines = [
                f"Name: {definition.name}",
            ]

            if definition.description:
                lines.append(
                    "Description: "
                    f"{definition.description}"
                )

            if definition.arguments:
                lines.append(
                    "Arguments:"
                )

                for name, description in sorted(
                    definition.arguments.items()
                ):
                    lines.append(
                        f"- {name}: {description}"
                    )
            else:
                lines.append(
                    "Arguments: none"
                )

            sections.append(
                "\n".join(
                    lines
                )
            )

        capability_text = "\n\n".join(
            sections
        )

        return (
            "You are the planning component for JarvisAI.\n"
            "Convert the user request into the smallest safe ordered "
            "sequence of allowed capabilities.\n\n"
            "Allowed capabilities:\n"
            f"{capability_text}\n\n"
            "Rules:\n"
            "- Use only capabilities from the allowed list.\n"
            "- Never invent a capability.\n"
            "- Preserve execution order.\n"
            "- Use the minimum number of steps needed.\n"
            "- Do not execute anything. Only produce a plan.\n"
            "- If no valid plan can be produced, return an empty "
            "steps list.\n"
            "- Return JSON only.\n\n"
            "Required JSON format:\n"
            '{"steps":[{"capability":"name","arguments":{}}]}\n\n'
            f"User request:\n{text}"
        )

    @staticmethod
    def _parse_response(
        response: str,
    ) -> dict[str, Any] | None:
        response = response.strip()

        if not response:
            return None

        if response.startswith(
            "```"
        ):
            lines = response.splitlines()

            if lines:
                lines = lines[1:]

            if (
                lines
                and lines[-1].strip() == "```"
            ):
                lines = lines[:-1]

            response = "\n".join(
                lines
            ).strip()

        try:
            data = json.loads(
                response
            )
        except json.JSONDecodeError:
            return None

        if not isinstance(
            data,
            dict,
        ):
            return None

        return data
