import pytest

from jarvis.planner.context import ExecutionContext


def test_context_stores_step_output() -> None:
    context = ExecutionContext()

    context.set_output(
        1,
        {
            "device_id": "abc123",
        },
    )

    assert context.has_output(
        1
    )
    assert context.get_output(
        1
    ) == {
        "device_id": "abc123",
    }


def test_context_rejects_invalid_step_index() -> None:
    context = ExecutionContext()

    with pytest.raises(
        ValueError,
        match="at least 1",
    ):
        context.set_output(
            0,
            "x",
        )


def test_context_raises_for_missing_output() -> None:
    context = ExecutionContext()

    with pytest.raises(
        KeyError,
        match="No output",
    ):
        context.get_output(
            2
        )
