from __future__ import annotations

import pytest

from jarvis.agent.memory_repository import AIAgentMemoryRepository


class Row(dict):
    pass


def base_row() -> Row:
    return Row(
        goal="Check Jarvis",
        capabilities_json='["system.ping"]',
        success=1,
        completed_steps=1,
        failed_steps=0,
        reflection_decision="complete",
        created_at="2026-08-05T10:00:00+00:00",
        metadata_json='{"source":"test"}',
    )


def test_repository_rejects_non_list_capabilities_json() -> None:
    row = base_row()
    row["capabilities_json"] = '{"wrong":"shape"}'

    with pytest.raises(
        TypeError,
        match="capabilities",
    ):
        AIAgentMemoryRepository._row_to_record(
            row,  # type: ignore[arg-type]
        )


def test_repository_rejects_non_object_metadata_json() -> None:
    row = base_row()
    row["metadata_json"] = '["wrong", "shape"]'

    with pytest.raises(
        TypeError,
        match="metadata",
    ):
        AIAgentMemoryRepository._row_to_record(
            row,  # type: ignore[arg-type]
        )
