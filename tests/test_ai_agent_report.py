from jarvis.agent.report import (
    AIAgentRunReportBuilder,
)
from jarvis.agent.runtime import (
    AIAgentRunResult,
    AIAgentRunStatus,
)


def test_agent_report_handles_no_plan() -> None:
    report = AIAgentRunReportBuilder().build(
        AIAgentRunResult(
            status=AIAgentRunStatus.NO_PLAN,
            preview=None,
            execution=None,
            reflection=None,
            memory_record=None,
        )
    )

    assert (
        "status=no_plan"
        in report.summary
    )
    assert report.lines == (
        "No executable AI plan was produced.",
    )
