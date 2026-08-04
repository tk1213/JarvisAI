from __future__ import annotations

import pytest

from jarvis.skills.context import SkillContext
from jarvis.skills.loader import SkillLoader
from jarvis.skills.manager import SkillManager


@pytest.mark.asyncio
async def test_system_skill_execute(
    skill_context: SkillContext,
) -> None:
    manager = SkillManager()

    loader = SkillLoader(
        manager=manager,
        context=skill_context,
    )

    loader.load_package(
        "jarvis.skills.builtin",
    )

    result = await manager.execute(
        "system.ping",
    )

    assert result["status"] == "ok"


@pytest.mark.asyncio
async def test_system_version(
    skill_context: SkillContext,
) -> None:
    manager = SkillManager()

    loader = SkillLoader(
        manager=manager,
        context=skill_context,
    )

    loader.load_package(
        "jarvis.skills.builtin",
    )

    result = await manager.execute(
        "system.version",
    )

    assert "jarvis" in result


@pytest.mark.asyncio
async def test_system_health(
    skill_context: SkillContext,
) -> None:
    manager = SkillManager()

    loader = SkillLoader(
        manager=manager,
        context=skill_context,
    )

    loader.load_package(
        "jarvis.skills.builtin",
    )

    result = await manager.execute(
        "system.health",
    )

    assert result["healthy"] is True


def test_list_capabilities(
    skill_context: SkillContext,
) -> None:
    manager = SkillManager()

    loader = SkillLoader(
        manager=manager,
        context=skill_context,
    )

    loader.load_package(
        "jarvis.skills.builtin",
    )

    assert manager.list_capabilities() == [
        "smart_home.list_devices",
        "smart_home.status",
        "smart_home.toggle",
        "smart_home.turn_off",
        "smart_home.turn_on",
        "system.execution_history",
        "system.health",
        "system.ping",
        "system.version",
    ]


def test_list_capability_definitions(
    skill_context: SkillContext,
) -> None:
    manager = SkillManager()

    loader = SkillLoader(
        manager=manager,
        context=skill_context,
    )

    loader.load_package(
        "jarvis.skills.builtin",
    )

    definitions = manager.list_capability_definitions()

    assert [
        definition.name
        for definition in definitions
    ] == [
        "smart_home.list_devices",
        "smart_home.status",
        "smart_home.toggle",
        "smart_home.turn_off",
        "smart_home.turn_on",
        "system.execution_history",
        "system.health",
        "system.ping",
        "system.version",
    ]

    definitions_by_name = {
        definition.name: definition
        for definition in definitions
    }

    assert (
        definitions_by_name[
            "system.health"
        ].description
        == "Check the current health status of JarvisAI."
    )

    assert (
        definitions_by_name[
            "system.ping"
        ].description
        == "Check whether JarvisAI is running and responding."
    )

    assert (
        definitions_by_name[
            "system.version"
        ].description
        == "Get the current JarvisAI version."
    )

    assert (
        definitions_by_name[
            "smart_home.list_devices"
        ].description
        == (
            "List all smart home devices currently "
            "available to JarvisAI."
        )
    )

    device_query_argument = {
        "device_query": (
            "Natural-language device description from the user, "
            "such as 'ไฟห้องนั่งเล่น', 'bedroom light', "
            "or 'garage door'. Do not invent a device ID."
        ),
    }

    assert (
        definitions_by_name[
            "smart_home.status"
        ].arguments
        == device_query_argument
    )

    assert (
        definitions_by_name[
            "smart_home.turn_on"
        ].arguments
        == device_query_argument
    )

    assert (
        definitions_by_name[
            "smart_home.turn_off"
        ].arguments
        == device_query_argument
    )

    assert (
        definitions_by_name[
            "smart_home.toggle"
        ].arguments
        == device_query_argument
    )