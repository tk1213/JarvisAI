from __future__ import annotations

from typing import Any

import pytest

from jarvis.planner.executor import PlanExecutor
from jarvis.planner.models import (
    Plan,
    PlanStatus,
    PlanStep,
)
from jarvis.planner.orchestrator import PlannerOrchestrator
from jarvis.planner.service import PlannerService


class StubGenerator:
    def __init__(
        self,
        plan: Plan | None,
    ) -> None:
        self.plan = plan

    async def generate(
        self,
        text: str,
    ) -> Plan | None:
        del text
        return self.plan


class StubRegistry:
    def __init__(
        self,
        allowed: set[str],
    ) -> None:
        self.allowed = allowed

    def is_allowed(
        self,
        capability: str,
    ) -> bool:
        return capability in self.allowed


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
            "ok": True,
        }


def build(
    plan: Plan,
) -> tuple[
    PlannerOrchestrator,
    StubRouter,
]:
    registry = StubRegistry(
        {
            step.capability
            for step in plan.steps
        }
    )
    planner = PlannerService(
        registry,  # type: ignore[arg-type]
    )
    router = StubRouter()
    executor = PlanExecutor(
        router,  # type: ignore[arg-type]
    )

    orchestrator = PlannerOrchestrator(
        generator=StubGenerator(plan),  # type: ignore[arg-type]
        planner=planner,
        executor=executor,
    )

    return orchestrator, router


@pytest.mark.asyncio
async def test_read_only_plan_can_execute_without_confirmation() -> None:
    plan = Plan(
        goal="Check status",
        steps=[
            PlanStep(
                index=1,
                capability="smart_home.status",
            )
        ],
        status=PlanStatus.READY,
    )

    orchestrator, router = build(
        plan
    )

    preview = await orchestrator.prepare(
        "Check status"
    )

    assert preview is not None
    assert preview.requires_confirmation is False

    result = await orchestrator.execute_preview(
        preview
    )

    assert result.success is True
    assert router.calls == [
        "smart_home.status",
    ]


@pytest.mark.asyncio
async def test_side_effect_plan_requires_confirmation() -> None:
    plan = Plan(
        goal="Turn off light",
        steps=[
            PlanStep(
                index=1,
                capability="smart_home.turn_off",
            )
        ],
        status=PlanStatus.READY,
    )

    orchestrator, router = build(
        plan
    )

    preview = await orchestrator.prepare(
        "Turn off light"
    )

    assert preview is not None
    assert preview.requires_confirmation is True
    assert orchestrator.has_pending_plan is True
    assert router.calls == []

    with pytest.raises(
        PermissionError,
        match="requires confirmation",
    ):
        await orchestrator.execute_preview(
            preview
        )


@pytest.mark.asyncio
async def test_confirm_executes_pending_plan() -> None:
    plan = Plan(
        goal="Turn off light",
        steps=[
            PlanStep(
                index=1,
                capability="smart_home.turn_off",
            )
        ],
        status=PlanStatus.READY,
    )

    orchestrator, router = build(
        plan
    )

    await orchestrator.prepare(
        "Turn off light"
    )

    result = await orchestrator.confirm_pending()

    assert result.success is True
    assert orchestrator.has_pending_plan is False
    assert router.calls == [
        "smart_home.turn_off",
    ]


@pytest.mark.asyncio
async def test_cancel_pending_plan() -> None:
    plan = Plan(
        goal="Turn off light",
        steps=[
            PlanStep(
                index=1,
                capability="smart_home.turn_off",
            )
        ],
        status=PlanStatus.READY,
    )

    orchestrator, router = build(
        plan
    )

    await orchestrator.prepare(
        "Turn off light"
    )

    assert orchestrator.cancel_pending() is True
    assert orchestrator.has_pending_plan is False
    assert router.calls == []
