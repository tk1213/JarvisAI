from __future__ import annotations

from jarvis.planner.risk import (
    PlanRiskLevel,
    PlanRiskPolicy,
)
from jarvis.tools.contracts import (
    ToolCall,
    ToolError,
    ToolResult,
)
from jarvis.tools.definitions import (
    ToolDefinition,
    ToolDefinitionFactory,
)
from jarvis.tools.executor import ToolExecutor


class ReadOnlyToolDefinitionFactory(
    ToolDefinitionFactory
):
    def __init__(
        self,
        *args,
        risk_policy: PlanRiskPolicy | None = None,
        **kwargs,
    ) -> None:
        super().__init__(
            *args,
            **kwargs,
        )

        self._risk_policy = (
            risk_policy
            if risk_policy is not None
            else PlanRiskPolicy()
        )

    def list_definitions(
        self,
    ) -> list[ToolDefinition]:
        definitions = (
            super().list_definitions()
        )

        safe_definitions: list[
            ToolDefinition
        ] = []

        for definition in definitions:
            capability_name = (
                self.resolve_capability_name(
                    definition.name
                )
            )

            if capability_name is None:
                continue

            if (
                self._risk_policy.classify(
                    capability_name
                )
                is PlanRiskLevel.READ_ONLY
            ):
                safe_definitions.append(
                    definition
                )

        return safe_definitions


class ReadOnlyToolExecutor(
    ToolExecutor
):
    def __init__(
        self,
        *args,
        risk_policy: PlanRiskPolicy | None = None,
        **kwargs,
    ) -> None:
        super().__init__(
            *args,
            **kwargs,
        )

        self._risk_policy = (
            risk_policy
            if risk_policy is not None
            else PlanRiskPolicy()
        )

    async def execute(
        self,
        call: ToolCall,
    ) -> ToolResult:
        if (
            self._risk_policy.classify(
                call.name
            )
            is PlanRiskLevel.SIDE_EFFECT
        ):
            return ToolResult(
                name=call.name,
                success=False,
                call_id=call.call_id,
                error=ToolError(
                    code="tool_requires_confirmation",
                    message=(
                        "This tool can change system state and "
                        "must be executed through the confirmed "
                        "planner path."
                    ),
                ),
            )

        return await super().execute(
            call
        )
