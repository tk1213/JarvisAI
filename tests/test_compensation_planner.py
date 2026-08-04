from jarvis.planner.compensation import (
    CompensationPlanner,
    CompensationStatus,
)
from jarvis.planner.executor import (
    PlanExecutionResult,
    PlanStepResult,
)
from jarvis.planner.models import (
    Plan,
    PlanStatus,
    PlanStep,
    PlanStepStatus,
)


def test_successful_plan_needs_no_compensation() -> None:
    plan = Plan(
        goal="Ping",
        steps=[
            PlanStep(
                index=1,
                capability="system.ping",
                status=PlanStepStatus.COMPLETED,
            )
        ],
        status=PlanStatus.COMPLETED,
    )

    execution = PlanExecutionResult(
        plan=plan,
        step_results=[
            PlanStepResult(
                step_index=1,
                capability="system.ping",
                status=PlanStepStatus.COMPLETED,
            )
        ],
    )

    result = CompensationPlanner().build(
        execution
    )

    assert (
        result.status
        is CompensationStatus.NOT_REQUIRED
    )
    assert result.candidates == ()


def test_failed_plan_collects_completed_side_effects() -> None:
    plan = Plan(
        goal="Change device then inspect",
        steps=[
            PlanStep(
                index=1,
                capability="smart_home.turn_off",
                arguments={
                    "device_query": "Smart Plug 1",
                },
                status=PlanStepStatus.COMPLETED,
            ),
            PlanStep(
                index=2,
                capability="system.ping",
                status=PlanStepStatus.FAILED,
            ),
        ],
        status=PlanStatus.FAILED,
    )

    execution = PlanExecutionResult(
        plan=plan,
        step_results=[
            PlanStepResult(
                step_index=1,
                capability="smart_home.turn_off",
                status=PlanStepStatus.COMPLETED,
                output={
                    "status": "off",
                },
            ),
            PlanStepResult(
                step_index=2,
                capability="system.ping",
                status=PlanStepStatus.FAILED,
                error="temporary failure",
            ),
        ],
    )

    result = CompensationPlanner().build(
        execution
    )

    assert (
        result.status
        is CompensationStatus.REQUIRES_REVIEW
    )
    assert len(
        result.candidates
    ) == 1
    assert (
        result.candidates[0].capability
        == "smart_home.turn_off"
    )


def test_read_only_completed_steps_are_not_candidates() -> None:
    plan = Plan(
        goal="Read then fail",
        steps=[
            PlanStep(
                index=1,
                capability="system.version",
                status=PlanStepStatus.COMPLETED,
            ),
            PlanStep(
                index=2,
                capability="system.ping",
                status=PlanStepStatus.FAILED,
            ),
        ],
        status=PlanStatus.FAILED,
    )

    execution = PlanExecutionResult(
        plan=plan,
        step_results=[
            PlanStepResult(
                step_index=1,
                capability="system.version",
                status=PlanStepStatus.COMPLETED,
            ),
            PlanStepResult(
                step_index=2,
                capability="system.ping",
                status=PlanStepStatus.FAILED,
                error="invalid request",
            ),
        ],
    )

    result = CompensationPlanner().build(
        execution
    )

    assert (
        result.status
        is CompensationStatus.NOT_REQUIRED
    )
    assert result.candidates == ()


def test_candidates_are_returned_in_reverse_execution_order() -> None:
    plan = Plan(
        goal="Two changes then fail",
        steps=[
            PlanStep(
                index=1,
                capability="smart_home.turn_on",
                arguments={
                    "device_query": "Light 1",
                },
                status=PlanStepStatus.COMPLETED,
            ),
            PlanStep(
                index=2,
                capability="smart_home.turn_off",
                arguments={
                    "device_query": "Plug 1",
                },
                status=PlanStepStatus.COMPLETED,
            ),
            PlanStep(
                index=3,
                capability="system.ping",
                status=PlanStepStatus.FAILED,
            ),
        ],
        status=PlanStatus.FAILED,
    )

    execution = PlanExecutionResult(
        plan=plan,
        step_results=[
            PlanStepResult(
                step_index=1,
                capability="smart_home.turn_on",
                status=PlanStepStatus.COMPLETED,
            ),
            PlanStepResult(
                step_index=2,
                capability="smart_home.turn_off",
                status=PlanStepStatus.COMPLETED,
            ),
            PlanStepResult(
                step_index=3,
                capability="system.ping",
                status=PlanStepStatus.FAILED,
                error="failure",
            ),
        ],
    )

    result = CompensationPlanner().build(
        execution
    )

    assert [
        candidate.step_index
        for candidate in result.candidates
    ] == [
        2,
        1,
    ]
