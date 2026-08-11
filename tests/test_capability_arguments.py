from __future__ import annotations

import pytest

from jarvis.services.capability import CapabilityArgument


def test_structured_argument_defaults_to_optional_string() -> None:
    argument = CapabilityArgument(
        description="Device name",
    )

    assert argument.type == "string"
    assert argument.required is False
    assert str(argument) == "Device name"
    assert argument.to_json_schema() == {
        "type": "string",
        "description": "Device name",
    }


def test_structured_argument_builds_rich_schema() -> None:
    argument = CapabilityArgument(
        description="Number of records",
        type="integer",
        required=True,
        enum=(1, 5, 10),
        minimum=1,
        maximum=10,
    )

    assert argument.to_json_schema() == {
        "type": "integer",
        "description": "Number of records",
        "enum": [1, 5, 10],
        "minimum": 1,
        "maximum": 10,
    }


def test_array_argument_supports_item_type() -> None:
    argument = CapabilityArgument(
        type="array",
        items_type="string",
    )

    assert argument.to_json_schema() == {
        "type": "array",
        "items": {
            "type": "string",
        },
    }


def test_items_type_is_rejected_for_non_array() -> None:
    with pytest.raises(
        ValueError,
        match="only valid for arrays",
    ):
        CapabilityArgument(
            type="string",
            items_type="string",
        )


def test_invalid_numeric_bounds_are_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="minimum cannot exceed maximum",
    ):
        CapabilityArgument(
            type="number",
            minimum=10,
            maximum=1,
        )
