from __future__ import annotations

from jarvis.services.capability import CapabilityRequest
from jarvis.tools.contracts import ToolCall


class CapabilityToolAdapter:
    @staticmethod
    def to_capability_request(
        call: ToolCall,
    ) -> CapabilityRequest:
        return CapabilityRequest(
            capability=call.name,
            arguments=dict(
                call.arguments
            ),
        )

    @staticmethod
    def from_capability_request(
        request: CapabilityRequest,
        *,
        call_id: str | None = None,
    ) -> ToolCall:
        return ToolCall(
            name=request.capability,
            arguments=dict(
                request.arguments
            ),
            call_id=call_id,
        )
