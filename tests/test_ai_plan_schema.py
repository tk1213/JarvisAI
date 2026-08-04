import pytest

from jarvis.planner.ai_plan_schema import (
    build_ai_plan_json_schema,
)


def test_schema_has_strict_plan_shape() -> None:
    schema = build_ai_plan_json_schema(
        max_steps=8
    )

    assert schema["type"] == "object"
    assert schema["additionalProperties"] is False
    assert schema["properties"]["steps"]["maxItems"] == 8
    assert schema["properties"]["steps"]["minItems"] == 1


def test_schema_rejects_invalid_max_steps() -> None:
    with pytest.raises(
        ValueError,
        match="at least 1",
    ):
        build_ai_plan_json_schema(
            max_steps=0
        )
