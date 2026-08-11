from __future__ import annotations

from unittest.mock import Mock

from jarvis.agent.conversation_bridge import (
    AIAgentConversationBridge,
)
from jarvis.agent.runtime import AIAgentRuntime
from jarvis.planner.ai_plan_memory import AIPlanMemoryStore
from jarvis.planner.ai_plan_reflection import (
    AIPlanReflectionService,
)
from jarvis.planner.orchestrator import PlannerOrchestrator


def test_runtime_exposes_pending_plan_state() -> None:
    orchestrator = Mock(
        spec=PlannerOrchestrator
    )

    orchestrator.has_pending_plan = True

    runtime = AIAgentRuntime(
        orchestrator=orchestrator,
        reflection=AIPlanReflectionService(),
        memory=AIPlanMemoryStore(),
    )

    assert runtime.has_pending_plan is True


def test_bridge_uses_runtime_pending_contract() -> None:
    runtime = Mock(
        spec=AIAgentRuntime
    )

    runtime.has_pending_plan = True

    bridge = AIAgentConversationBridge(
        runtime
    )

    assert bridge.has_pending_plan is True
