from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pytest

from jarvis.planner.execution_policy import ExecutionPolicy
from jarvis.planner.models import (
    Plan,
    PlanStatus,
    PlanStep,
)
from jarvis.services.capability import CapabilityDefinition
from jarvis.services.capability_registry import CapabilityRegistry
from jarvis.tools.contracts import ToolCall
from jarvis.tools.safe import (
    ReadOnlyToolDefinitionFactory,
    ReadOnlyToolExecutor,
)


class StubRouter:
    def __init__(self) -> None:
        self.calls: list[str] = []

    async def execute_request(
        self,
        request,
    ) -> Any:
        self.calls.append(
            request.capability
        )

        return {
            "capability": request.capability,
            "arguments": request.arguments,
            "ok": True,
        }


def build_registry() -> CapabilityRegistry:
    return CapabilityRegistry(
        [
            CapabilityDefinition(
                name="smart_home.list_devices",
                description="List devices.",
            ),
            CapabilityDefinition(
                name="smart_home.status",
                description="Read device status.",
                arguments={
                    "device_query": "Device description",
                },
            ),
            CapabilityDefinition(
                name="smart_home.toggle",
                description="Toggle device.",
                arguments={
                    "device_query": "Device description",
                },
            ),
            CapabilityDefinition(
                name="smart_home.turn_off",
                description="Turn off device.",
                arguments={
                    "device_query": "Device description",
                },
            ),
            CapabilityDefinition(
                name="smart_home.turn_on",
                description="Turn on device.",
                arguments={
                    "device_query": "Device description",
                },
            ),
            CapabilityDefinition(
                name="system.health",
                description="Check health.",
            ),
            CapabilityDefinition(
                name="system.ping",
                description="Ping Jarvis.",
            ),
            CapabilityDefinition(
                name="system.version",
                description="Read version.",
            ),
        ]
    )


def test_native_tool_schema_exposes_only_read_only_capabilities() -> None:
    factory = ReadOnlyToolDefinitionFactory(
        build_registry()
    )

    names = [
        tool.name
        for tool in factory.list_definitions()
    ]

    assert names == [
        "smart_home_list_devices",
        "smart_home_status",
        "system_health",
        "system_ping",
        "system_version",
    ]


@pytest.mark.asyncio
async def test_native_executor_allows_read_only_capability() -> None:
    registry = build_registry()
    router = StubRouter()

    executor = ReadOnlyToolExecutor(
        registry=registry,
        router=router,  # type: ignore[arg-type]
    )

    result = await executor.execute(
        ToolCall(
            name="system.ping",
            call_id="read-only-1",
        )
    )

    assert result.success is True
    assert router.calls == [
        "system.ping",
    ]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "capability",
    [
        "smart_home.toggle",
        "smart_home.turn_off",
        "smart_home.turn_on",
    ],
)
async def test_native_executor_blocks_state_changes(
    capability: str,
) -> None:
    registry = build_registry()
    router = StubRouter()

    executor = ReadOnlyToolExecutor(
        registry=registry,
        router=router,  # type: ignore[arg-type]
    )

    result = await executor.execute(
        ToolCall(
            name=capability,
            arguments={
                "device_query": "Smart Plug 1",
            },
        )
    )

    assert result.success is False
    assert result.error is not None
    assert (
        result.error.code
        == "tool_requires_confirmation"
    )
    assert router.calls == []


def test_read_only_multi_step_plan_needs_no_confirmation() -> None:
    plan = Plan(
        goal="Check Jarvis and device status",
        steps=[
            PlanStep(
                index=1,
                capability="system.health",
            ),
            PlanStep(
                index=2,
                capability="smart_home.status",
                arguments={
                    "device_query": "Smart Plug 1",
                },
            ),
        ],
        status=PlanStatus.READY,
    )

    decision = ExecutionPolicy().evaluate(
        plan
    )

    assert decision.requires_confirmation is False


def test_mixed_multi_step_plan_requires_confirmation() -> None:
    plan = Plan(
        goal="Turn off plug and verify status",
        steps=[
            PlanStep(
                index=1,
                capability="smart_home.turn_off",
                arguments={
                    "device_query": "Smart Plug 1",
                },
            ),
            PlanStep(
                index=2,
                capability="smart_home.status",
                arguments={
                    "device_query": "Smart Plug 1",
                },
            ),
        ],
        status=PlanStatus.READY,
    )

    decision = ExecutionPolicy().evaluate(
        plan
    )

    assert decision.requires_confirmation is True
    assert decision.side_effect_steps == (1,)


@dataclass
class UnknownCapabilityCase:
    capability: str


@pytest.mark.parametrize(
    "case",
    [
        UnknownCapabilityCase(
            capability="future.device.calibrate"
        ),
        UnknownCapabilityCase(
            capability="future.automation.run"
        ),
    ],
)
def test_unknown_future_actions_fail_closed(
    case: UnknownCapabilityCase,
) -> None:
    plan = Plan(
        goal="Future action",
        steps=[
            PlanStep(
                index=1,
                capability=case.capability,
            )
        ],
        status=PlanStatus.READY,
    )

    decision = ExecutionPolicy().evaluate(
        plan
    )

    assert decision.requires_confirmation is True
