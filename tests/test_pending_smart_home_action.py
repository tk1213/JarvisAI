from __future__ import annotations

import pytest

from jarvis.smart_home.device import SmartDevice
from jarvis.smart_home.pending_action import (
    PendingSmartHomeAction,
    PendingSmartHomeActionStore,
    SmartHomeAction,
)


def make_device(
    device_id: str,
    name: str,
) -> SmartDevice:
    return SmartDevice(
        id=device_id,
        name=name,
        room="",
        device_type="cz",
        online=True,
        power=False,
    )


def test_pending_action() -> None:
    first = make_device(
        "plug001",
        "Living Room Smart Plug",
    )

    second = make_device(
        "plug002",
        "Bedroom Smart Plug",
    )

    pending = PendingSmartHomeAction(
        action=SmartHomeAction.TURN_ON,
        candidates=(
            first,
            second,
        ),
    )

    assert (
        pending.action
        is SmartHomeAction.TURN_ON
    )

    assert pending.candidates == (
        first,
        second,
    )


def test_pending_requires_multiple_candidates() -> None:
    device = make_device(
        "plug001",
        "Smart Plug",
    )

    with pytest.raises(
        ValueError,
        match="at least two candidate devices",
    ):
        PendingSmartHomeAction(
            action=SmartHomeAction.TURN_ON,
            candidates=(device,),
        )


def test_store_starts_empty() -> None:
    store = PendingSmartHomeActionStore()

    assert not store.has_pending
    assert store.pending is None


def test_store_set_and_clear() -> None:
    first = make_device(
        "plug001",
        "Living Room Smart Plug",
    )

    second = make_device(
        "plug002",
        "Bedroom Smart Plug",
    )

    pending = PendingSmartHomeAction(
        action=SmartHomeAction.TURN_OFF,
        candidates=(
            first,
            second,
        ),
    )

    store = PendingSmartHomeActionStore()

    store.set(
        pending
    )

    assert store.has_pending
    assert store.pending == pending

    store.clear()

    assert not store.has_pending
    assert store.pending is None


def test_store_consume() -> None:
    first = make_device(
        "plug001",
        "Living Room Smart Plug",
    )

    second = make_device(
        "plug002",
        "Bedroom Smart Plug",
    )

    pending = PendingSmartHomeAction(
        action=SmartHomeAction.STATUS,
        candidates=(
            first,
            second,
        ),
    )

    store = PendingSmartHomeActionStore()

    store.set(
        pending
    )

    consumed = store.consume()

    assert consumed == pending
    assert not store.has_pending
    assert store.pending is None