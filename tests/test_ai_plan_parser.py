import pytest

from jarvis.planner.ai_plan_parser import (
    AIPlanParseError,
    AIPlanParser,
)


def test_parser_accepts_json_text() -> None:
    draft = AIPlanParser().parse(
        """
        {
          "goal": "Check Jarvis",
          "reasoning_summary": "Use read-only health.",
          "steps": [
            {
              "capability": "system.health",
              "arguments": {},
              "description": "Check health"
            }
          ]
        }
        """
    )

    assert draft.goal == "Check Jarvis"
    assert len(
        draft.steps
    ) == 1
    assert draft.steps[0].capability == "system.health"


def test_parser_accepts_dictionary() -> None:
    draft = AIPlanParser().parse(
        {
            "goal": "Ping Jarvis",
            "steps": [
                {
                    "capability": "system.ping",
                    "arguments": {},
                }
            ],
        }
    )

    assert draft.steps[0].arguments == {}


def test_parser_rejects_invalid_json() -> None:
    with pytest.raises(
        AIPlanParseError,
        match="valid JSON",
    ):
        AIPlanParser().parse(
            "{invalid"
        )


def test_parser_rejects_non_object_step() -> None:
    with pytest.raises(
        AIPlanParseError,
        match="step 1 must be an object",
    ):
        AIPlanParser().parse(
            {
                "goal": "Ping",
                "steps": [
                    "system.ping"
                ],
            }
        )


def test_parser_rejects_excessive_steps() -> None:
    with pytest.raises(
        AIPlanParseError,
        match="maximum step count",
    ):
        AIPlanParser(
            max_steps=1
        ).parse(
            {
                "goal": "Too many",
                "steps": [
                    {
                        "capability": "system.ping",
                        "arguments": {},
                    },
                    {
                        "capability": "system.health",
                        "arguments": {},
                    },
                ],
            }
        )
