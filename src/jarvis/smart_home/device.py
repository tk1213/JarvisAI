from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class SmartDevice:
    """
    Generic smart-home device model.
    """

    id: str
    name: str
    room: str
    device_type: str

    online: bool = True
    power: bool = False