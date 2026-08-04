from __future__ import annotations

from jarvis.services.capability_registry import CapabilityRegistry
from jarvis.services.capability_router import CapabilityRouter
from jarvis.tools.adapter import CapabilityToolAdapter
from jarvis.tools.contracts import (
    ToolCall,
    ToolError,
    ToolResult,
)


class ToolExecutor:
    def __init__(
        self,
        *,
        registry: CapabilityRegistry,
        router: CapabilityRouter,
    ) -> None:
        self._registry = registry
        self._router = router

    async def execute(
        self,
        call: ToolCall,
    ) -> ToolResult:
        if not self._registry.is_allowed(
            call.name
        ):
            return ToolResult(
                name=call.name,
                success=False,
                call_id=call.call_id,
                error=ToolError(
                    code="tool_not_allowed",
                    message=(
                        "Tool is not allowed: "
                        f"{call.name}"
                    ),
                ),
            )

        request = CapabilityToolAdapter.to_capability_request(
            call
        )

        try:
            output = await self._router.execute_request(
                request
            )
        except Exception as exc:  # noqa: BLE001
            return ToolResult(
                name=call.name,
                success=False,
                call_id=call.call_id,
                error=ToolError(
                    code="tool_execution_failed",
                    message=str(
                        exc
                    ),
                ),
            )

        return ToolResult(
            name=call.name,
            success=True,
            output=output,
            call_id=call.call_id,
        )
