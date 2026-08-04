import pytest

from jarvis.planner.context import ExecutionContext
from jarvis.planner.references import StepValueResolver


def test_resolves_entire_previous_step_output() -> None:
    context = ExecutionContext()
    context.set_output(
        1,
        {
            "device_id": "abc123",
        },
    )

    resolver = StepValueResolver()

    result = resolver.resolve_value(
        {
            "$step": "1",
        },
        context=context,
    )

    assert result == {
        "device_id": "abc123",
    }


def test_resolves_nested_previous_step_output() -> None:
    context = ExecutionContext()
    context.set_output(
        1,
        {
            "device": {
                "id": "abc123",
            }
        },
    )

    resolver = StepValueResolver()

    result = resolver.resolve_value(
        {
            "$step": "1.device.id",
        },
        context=context,
    )

    assert result == "abc123"


def test_resolves_references_inside_arguments() -> None:
    context = ExecutionContext()
    context.set_output(
        1,
        {
            "device_id": "abc123",
        },
    )

    resolver = StepValueResolver()

    result = resolver.resolve_arguments(
        {
            "device_id": {
                "$step": "1.device_id",
            },
            "mode": "status",
        },
        context=context,
    )

    assert result == {
        "device_id": "abc123",
        "mode": "status",
    }


def test_missing_path_raises() -> None:
    context = ExecutionContext()
    context.set_output(
        1,
        {
            "device_id": "abc123",
        },
    )

    resolver = StepValueResolver()

    with pytest.raises(
        KeyError,
        match="path not found",
    ):
        resolver.resolve_value(
            {
                "$step": "1.missing",
            },
            context=context,
        )


def test_invalid_reference_step_number_raises() -> None:
    resolver = StepValueResolver()

    with pytest.raises(
        ValueError,
        match="step number",
    ):
        resolver.resolve_value(
            {
                "$step": "one.device_id",
            },
            context=ExecutionContext(),
        )
