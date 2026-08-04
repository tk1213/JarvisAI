from __future__ import annotations

import pytest

from jarvis.services.capability import (
    CapabilityDefinition,
    CapabilityRequest,
)


def test_capability_request() -> None:
    request = CapabilityRequest(
        capability="system.ping",
    )

    assert request.capability == "system.ping"
    assert request.arguments == {}


def test_capability_request_with_arguments() -> None:
    request = CapabilityRequest(
        capability="smart_home.light.turn_on",
        arguments={
            "room": "living_room",
        },
    )

    assert request.capability == "smart_home.light.turn_on"
    assert request.arguments == {
        "room": "living_room",
    }


def test_capability_request_trims_capability() -> None:
    request = CapabilityRequest(
        capability="  system.ping  ",
    )

    assert request.capability == "system.ping"


def test_capability_request_rejects_empty_capability() -> None:
    with pytest.raises(
        ValueError,
        match="Capability cannot be empty",
    ):
        CapabilityRequest(
            capability="   ",
        )

def test_capability_definition() -> None:
    definition = CapabilityDefinition(
        name="system.version",
        description="Get JarvisAI version.",
    )

    assert definition.name == "system.version"
    assert definition.description == "Get JarvisAI version."
    assert definition.arguments == {}


def test_capability_definition_with_arguments() -> None:
    definition = CapabilityDefinition(
        name="smart_home.light.turn_on",
        description="Turn on a smart light.",
        arguments={
            "room": "Room containing the light",
        },
    )

    assert definition.arguments == {
        "room": "Room containing the light",
    }


def test_capability_definition_trims_name() -> None:
    definition = CapabilityDefinition(
        name="  system.ping  ",
    )

    assert definition.name == "system.ping"


def test_capability_definition_rejects_empty_name() -> None:
    with pytest.raises(
        ValueError,
        match="Capability name cannot be empty",
    ):
        CapabilityDefinition(
            name="   ",
        )
