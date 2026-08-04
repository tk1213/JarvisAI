from __future__ import annotations

import pytest

from jarvis.services.capability import CapabilityDefinition
from jarvis.services.capability_registry import CapabilityRegistry


def test_register_capability() -> None:
    registry = CapabilityRegistry()

    registry.register("system.ping")

    assert registry.is_allowed("system.ping")


def test_initial_capabilities() -> None:
    registry = CapabilityRegistry(
        {
            "system.ping",
            "system.health",
            "system.version",
        }
    )

    assert len(registry) == 3
    assert "system.ping" in registry


def test_list_capabilities_is_sorted() -> None:
    registry = CapabilityRegistry(
        {
            "system.version",
            "system.ping",
            "system.health",
        }
    )

    assert registry.list_capabilities() == [
        "system.health",
        "system.ping",
        "system.version",
    ]


def test_unregister_capability() -> None:
    registry = CapabilityRegistry(
        {"system.ping"}
    )

    registry.unregister("system.ping")

    assert "system.ping" not in registry


def test_reject_empty_capability() -> None:
    registry = CapabilityRegistry()

    with pytest.raises(
        ValueError,
        match="Capability cannot be empty",
    ):
        registry.register("   ")

def test_from_capabilities() -> None:
    registry = CapabilityRegistry.from_capabilities(
        [
            "system.version",
            "system.ping",
            "system.health",
        ]
    )

    assert registry.list_capabilities() == [
        "system.health",
        "system.ping",
        "system.version",
    ]    

def test_register_capability_definition() -> None:
    registry = CapabilityRegistry()

    definition = CapabilityDefinition(
        name="system.version",
        description="Get the current JarvisAI version.",
    )

    registry.register(definition)

    assert registry.is_allowed("system.version")
    assert registry.get("system.version") == definition


def test_get_unknown_capability_returns_none() -> None:
    registry = CapabilityRegistry(
        {
            "system.version",
        }
    )

    assert registry.get("system.unknown") is None


def test_list_definitions() -> None:
    registry = CapabilityRegistry(
        [
            CapabilityDefinition(
                name="system.version",
                description="Get the current JarvisAI version.",
            ),
            CapabilityDefinition(
                name="system.health",
                description="Check JarvisAI system health.",
            ),
        ]
    )

    definitions = registry.list_definitions()

    assert [
        definition.name
        for definition in definitions
    ] == [
        "system.health",
        "system.version",
    ]

    assert definitions[0].description == (
        "Check JarvisAI system health."
    )

    assert definitions[1].description == (
        "Get the current JarvisAI version."
    )


def test_register_definition_with_arguments() -> None:
    registry = CapabilityRegistry()

    definition = CapabilityDefinition(
        name="smart_home.light.turn_on",
        description="Turn on a smart light.",
        arguments={
            "device": "Name or ID of the light device",
            "room": "Room containing the light",
        },
    )

    registry.register(definition)

    stored = registry.get(
        "smart_home.light.turn_on"
    )

    assert stored is not None
    assert stored.arguments == {
        "device": "Name or ID of the light device",
        "room": "Room containing the light",
    }    