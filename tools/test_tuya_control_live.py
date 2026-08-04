from __future__ import annotations

import asyncio

from jarvis.smart_home.tuya_adapter import TuyaAdapter


async def main() -> None:
    print("=" * 60)
    print(" JarvisAI - Tuya Live Device Control Test")
    print("=" * 60)

    adapter = TuyaAdapter()

    try:
        print()
        print("Connecting to Tuya Cloud...")

        await adapter.connect()

        print("Connected: PASS")

        print()
        print("Discovering devices...")

        devices = await adapter.list_devices()

        if not devices:
            print("No Tuya devices found.")
            return

        device = devices[0]

        print()
        print(f"Device : {device.name}")
        print(f"ID     : {device.id}")
        print(f"Type   : {device.device_type}")
        print(f"Power  : {device.power}")

        print()
        print("-" * 60)
        print(" TURN ON TEST")
        print("-" * 60)

        turn_on_result = await adapter.turn_on(
            device.id
        )

        print(
            f"turn_on() result : {turn_on_result}"
        )

        status = await adapter.get_status(
            device.id
        )

        power = adapter._extract_power_state(
            status
        )

        print(f"Power after ON   : {power}")

        if not power:
            raise RuntimeError(
                "Device did not turn on."
            )

        await asyncio.sleep(2)

        print()
        print("-" * 60)
        print(" TURN OFF TEST")
        print("-" * 60)

        turn_off_result = await adapter.turn_off(
            device.id
        )

        print(
            f"turn_off() result: {turn_off_result}"
        )

        status = await adapter.get_status(
            device.id
        )

        power = adapter._extract_power_state(
            status
        )

        print(f"Power after OFF  : {power}")

        if power:
            raise RuntimeError(
                "Device did not turn off."
            )

        print()
        print("Tuya live control: PASS")

    finally:
        print()
        print("Disconnecting...")

        await adapter.disconnect()

        print(
            f"Connected: {adapter.connected}"
        )

        print()
        print("=" * 60)
        print(" Test Complete")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())