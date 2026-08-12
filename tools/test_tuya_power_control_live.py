from __future__ import annotations

import asyncio

from jarvis.smart_home.service import SmartHomeService
from jarvis.smart_home.tuya_adapter import TuyaAdapter

TARGET_DEVICE_ID = "a3c26709c720729fa86jk8"


async def main() -> None:
    print("Sprint 7 — Tuya Controlled Power Live Gate")
    print("-" * 60)

    service = SmartHomeService(
        adapter=TuyaAdapter(),
    )

    original_power: bool | None = None
    connected = False

    try:
        print()
        print("Connecting to Tuya Cloud...")

        await service.connect()
        connected = True

        print("Connection: PASS")

        device = await service.get_device(
            TARGET_DEVICE_ID
        )

        if device is None:
            raise RuntimeError(
                "Target device was not found."
            )

        print()
        print("Target device")
        print("-" * 60)
        print(f"Name   : {device.name}")
        print(f"ID     : {device.id}")
        print(f"Type   : {device.device_type}")
        print(f"Online : {device.online}")
        print(f"Power  : {device.power}")

        if not device.online:
            raise RuntimeError(
                "Target device is offline."
            )

        original_power = device.power

        print()
        print("WARNING")
        print("-" * 60)
        print(
            "This test will change the physical "
            "power state of the device."
        )
        print(
            "The original state will be restored "
            "before the test exits."
        )
        print()

        confirmation = await asyncio.to_thread(
            input,
            'Type "YES" to continue: ',
        )

        if confirmation.strip() != "YES":
            print()
            print("Power-control test cancelled.")
            return

        target_power = not original_power

        print()
        print(
            "Changing power state: "
            f"{original_power} -> {target_power}"
        )

        if target_power:
            changed = await service.turn_on(
                TARGET_DEVICE_ID
            )
        else:
            changed = await service.turn_off(
                TARGET_DEVICE_ID
            )

        if not changed:
            raise RuntimeError(
                "Tuya command was sent, but the "
                "target state was not verified."
            )

        changed_device = await service.get_device(
            TARGET_DEVICE_ID
        )

        if changed_device is None:
            raise RuntimeError(
                "Target device disappeared after command."
            )

        print(
            "Verified changed state: "
            f"{changed_device.power}"
        )

        if changed_device.power is not target_power:
            raise RuntimeError(
                "Device state does not match "
                "the requested state."
            )

        print()
        print("Power transition: PASS")

        print()
        print(
            "Restoring original state: "
            f"{target_power} -> {original_power}"
        )

        if original_power:
            restored = await service.turn_on(
                TARGET_DEVICE_ID
            )
        else:
            restored = await service.turn_off(
                TARGET_DEVICE_ID
            )

        if not restored:
            raise RuntimeError(
                "Failed to verify restored power state."
            )

        restored_device = await service.get_device(
            TARGET_DEVICE_ID
        )

        if restored_device is None:
            raise RuntimeError(
                "Target device disappeared "
                "during restore verification."
            )

        if restored_device.power is not original_power:
            raise RuntimeError(
                "Original power state was not restored."
            )

        print(
            "Restored state verified: "
            f"{restored_device.power}"
        )

        print()
        print("Power restore: PASS")
        print("Tuya controlled power live gate: PASS")

    finally:
        if connected:
            print()
            print("Disconnecting...")

            await service.disconnect()

            print("Disconnected.")


if __name__ == "__main__":
    asyncio.run(
        main()
    )