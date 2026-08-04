from jarvis.planner.ai_generator import AIPlanGenerator
from jarvis.planner.executor import PlanExecutor
from jarvis.planner.service import PlannerService
from jarvis.services.ai_service import AIService
from jarvis.services.capability_registry import CapabilityRegistry
from jarvis.services.capability_router import CapabilityRouter


class StubSkillManager:
    async def execute(
        self,
        capability: str,
        **kwargs,
    ):
        return {
            "capability": capability,
            "arguments": kwargs,
        }


def test_planner_components_share_same_registry() -> None:
    registry = CapabilityRegistry(
        [
            "system.ping",
        ]
    )

    router = CapabilityRouter(
        skill_manager=StubSkillManager(),  # type: ignore[arg-type]
        registry=registry,
    )

    planner = PlannerService(
        registry
    )

    executor = PlanExecutor(
        router
    )

    generator = AIPlanGenerator(
        ai=AIService(),
        registry=registry,
        planner=planner,
    )

    assert planner._registry is registry
    assert router._registry is registry
    assert generator._registry is registry
    assert executor._router is router
