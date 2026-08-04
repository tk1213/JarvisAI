from __future__ import annotations

from typing import Any


def build_ai_plan_json_schema(
    *,
    max_steps: int = 20,
) -> dict[str, Any]:
    if max_steps < 1:
        raise ValueError(
            "max_steps must be at least 1."
        )

    return {
        "type": "object",
        "properties": {
            "goal": {
                "type": "string",
                "minLength": 1,
            },
            "reasoning_summary": {
                "type": "string",
            },
            "steps": {
                "type": "array",
                "minItems": 1,
                "maxItems": max_steps,
                "items": {
                    "type": "object",
                    "properties": {
                        "capability": {
                            "type": "string",
                            "minLength": 1,
                        },
                        "arguments": {
                            "type": "object",
                            "additionalProperties": True,
                        },
                        "description": {
                            "type": "string",
                        },
                    },
                    "required": [
                        "capability",
                        "arguments",
                    ],
                    "additionalProperties": False,
                },
            },
        },
        "required": [
            "goal",
            "steps",
        ],
        "additionalProperties": False,
    }
