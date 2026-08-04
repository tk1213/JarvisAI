from __future__ import annotations

import pytest

from jarvis.skills.builtin.smart_home_skill import SmartHomeSkill
from jarvis.skills.context import SkillContext


@pytest.fixture
def smart_home_skill(
    skill_context: SkillContext,
) -> SmartHomeSkill:
    return SmartHomeSkill(
        skill_context,
    )


@pytest.mark.asyncio
async def test_list_devices(
    smart_home_skill: SmartHomeSkill,
) -> None:
    result = await smart_home_skill.execute(
        "smart_home.list_devices",
    )

    assert len(result) == 5

    device_ids = {
        device["id"]
        for device in result
    }

    assert device_ids == {
        "light001",
        "light002",
        "fan001",
        "ac001",
        "garage001",
    }


@pytest.mark.asyncio
async def test_device_status(
    smart_home_skill: SmartHomeSkill,
) -> None:
    result = await smart_home_skill.execute(
        "smart_home.status",
        device_id="light001",
    )

    assert result["success"] is True
    assert result["device"]["id"] == "light001"
    assert result["device"]["power"] is False


@pytest.mark.asyncio
async def test_turn_on_device(
    smart_home_skill: SmartHomeSkill,
) -> None:
    result = await smart_home_skill.execute(
        "smart_home.turn_on",
        device_id="light001",
    )

    assert result["success"] is True
    assert result["device_id"] == "light001"
    assert result["power"] is True

    status = await smart_home_skill.execute(
        "smart_home.status",
        device_id="light001",
    )

    assert status["device"]["power"] is True


@pytest.mark.asyncio
async def test_turn_off_device(
    smart_home_skill: SmartHomeSkill,
) -> None:
    await smart_home_skill.execute(
        "smart_home.turn_on",
        device_id="light001",
    )

    result = await smart_home_skill.execute(
        "smart_home.turn_off",
        device_id="light001",
    )

    assert result["success"] is True
    assert result["power"] is False

    status = await smart_home_skill.execute(
        "smart_home.status",
        device_id="light001",
    )

    assert status["device"]["power"] is False


@pytest.mark.asyncio
async def test_toggle_device(
    smart_home_skill: SmartHomeSkill,
) -> None:
    result = await smart_home_skill.execute(
        "smart_home.toggle",
        device_id="fan001",
    )

    assert result["success"] is True
    assert result["power"] is True

    result = await smart_home_skill.execute(
        "smart_home.toggle",
        device_id="fan001",
    )

    assert result["success"] is True
    assert result["power"] is False


@pytest.mark.asyncio
async def test_device_not_found(
    smart_home_skill: SmartHomeSkill,
) -> None:
    result = await smart_home_skill.execute(
        "smart_home.status",
        device_id="does-not-exist",
    )

    assert result == {
        "success": False,
        "error": "device_not_found",
        "device_id": "does-not-exist",
    }


@pytest.mark.asyncio
async def test_missing_device_reference(
    smart_home_skill: SmartHomeSkill,
) -> None:
    with pytest.raises(
        ValueError,
        match="device_query or device_id is required",
    ):
        await smart_home_skill.execute(
            "smart_home.turn_on",
        )


@pytest.mark.asyncio
async def test_empty_device_id(
    smart_home_skill: SmartHomeSkill,
) -> None:
    with pytest.raises(
        ValueError,
        match="device_id is required",
    ):
        await smart_home_skill.execute(
            "smart_home.turn_on",
            device_id="   ",
        )


@pytest.mark.asyncio
async def test_unknown_command(
    smart_home_skill: SmartHomeSkill,
) -> None:
    with pytest.raises(
        ValueError,
        match="Unsupported command",
    ):
        await smart_home_skill.execute(
            "smart_home.unknown",
            device_id="light001",
        )