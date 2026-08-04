from __future__ import annotations

from dataclasses import dataclass

import pytest

from jarvis.planner.conversation_bridge import PlannerConversationBridge


@dataclass
class FakeStep:
    capability: str
    arguments: dict


@dataclass
class FakePlan:
    steps: list[FakeStep]


@dataclass
class FakePreview:
    plan: FakePlan
    requires_confirmation: bool


@dataclass
class FakeResult:
    success: bool
    step_results: list


class FakeOrchestrator:
    def __init__(self, preview=None) -> None:
        self.preview = preview
        self.has_pending_plan = False
        self.confirmed = False
        self.cancelled = False

    async def prepare(self, text):
        del text
        if self.preview and self.preview.requires_confirmation:
            self.has_pending_plan = True
        return self.preview

    async def execute_preview(self, preview):
        del preview
        return FakeResult(True, [])

    async def confirm_pending(self):
        self.confirmed = True
        self.has_pending_plan = False
        return FakeResult(True, [])

    def cancel_pending(self):
        self.cancelled = True
        self.has_pending_plan = False
        return True


@pytest.mark.asyncio
async def test_no_plan_falls_through() -> None:
    bridge = PlannerConversationBridge(FakeOrchestrator())
    result = await bridge.handle_ai_request("hello")
    assert result.handled is False


@pytest.mark.asyncio
async def test_read_only_executes() -> None:
    preview = FakePreview(
        FakePlan([FakeStep("system.health", {})]),
        False,
    )
    bridge = PlannerConversationBridge(FakeOrchestrator(preview))
    result = await bridge.handle_ai_request("check")
    assert result.handled is True
    assert "สำเร็จ" in result.reply


@pytest.mark.asyncio
async def test_side_effect_waits_for_confirmation() -> None:
    preview = FakePreview(
        FakePlan(
            [FakeStep("smart_home.turn_off", {"device": "light"})]
        ),
        True,
    )
    orchestrator = FakeOrchestrator(preview)
    bridge = PlannerConversationBridge(orchestrator)

    result = await bridge.handle_ai_request("turn off light")

    assert result.handled is True
    assert orchestrator.has_pending_plan is True
    assert "ยืนยัน" in result.reply


@pytest.mark.asyncio
async def test_pending_confirmation() -> None:
    orchestrator = FakeOrchestrator()
    orchestrator.has_pending_plan = True
    bridge = PlannerConversationBridge(orchestrator)

    result = await bridge.handle_pending("ยืนยัน")

    assert result.handled is True
    assert orchestrator.confirmed is True
