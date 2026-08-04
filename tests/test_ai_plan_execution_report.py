from jarvis.planner.ai_plan_adapter import (
    AIPlanAdaptationResult,
)
from jarvis.planner.ai_plan_contract import (
    AIPlanDraft,
    AIPlanStepDraft,
)
from jarvis.planner.ai_plan_execution import (
    AIPlanExecutionResult,
)
from jarvis.planner.ai_plan_execution_report import (
    AIPlanExecutionReportBuilder,
)
from jarvis.planner.ai_plan_pipeline import (
    AIPlanPipelineResult,
)
from jarvis.planner.ai_plan_validation import (
    AIPlanValidationResult,
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


def make_result() -> AIPlanExecutionResult:
    plan = Plan(
        goal="Check Jarvis",
        steps=[
            PlanStep(
                index=1,
                capability="system.ping",
                arguments={},
                description="Execute system.ping",
                status=PlanStepStatus.COMPLETED,
            )
        ],
        status=PlanStatus.COMPLETED,
    )

    validation = AIPlanValidationResult(
        valid=True,
        issues=(),
    )

    adaptation = AIPlanAdaptationResult(
        plan=plan,
        validation=validation,
    )

    pipeline = AIPlanPipelineResult(
        draft=AIPlanDraft(
            goal="Check Jarvis",
            steps=(
                AIPlanStepDraft(
                    capability="system.ping",
                ),
            ),
        ),
        adaptation=adaptation,
    )

    execution = PlanExecutionResult(
        plan=plan,
        step_results=[
            PlanStepResult(
                step_index=1,
                capability="system.ping",
                status=PlanStepStatus.COMPLETED,
                output={
                    "status": "ok",
                },
                attempts=1,
            )
        ],
    )

    return AIPlanExecutionResult(
        pipeline=pipeline,
        execution=execution,
    )


def test_execution_report_formats_result() -> None:
    report = AIPlanExecutionReportBuilder().build(
        make_result()
    )

    assert (
        "status=completed"
        in report.summary
    )
    assert (
        "completed_steps=1/1"
        in report.summary
    )
    assert report.lines == (
        (
            "1. system.ping: "
            "status=completed, attempts=1"
        ),
    )
