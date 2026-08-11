from __future__ import annotations

import pytest

from jarvis.skills.builtin.system_skill import SystemSkill


@pytest.mark.asyncio
async def test_system_datetime_returns_bangkok_time(
    skill_context,
) -> None:
    skill = SystemSkill(
        skill_context
    )

    result = await skill.execute(
        "system.datetime"
    )

    assert result["timezone"] == "Asia/Bangkok"
    assert isinstance(
        result["iso"],
        str,
    )
    assert isinstance(
        result["date"],
        str,
    )
    assert isinstance(
        result["time"],
        str,
    )
    assert isinstance(
        result["weekday"],
        str,
    )

    assert result["iso"].endswith(
        "+07:00"
    )