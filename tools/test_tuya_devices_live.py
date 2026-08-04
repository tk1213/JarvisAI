from __future__ import annotations

import asyncio

from jarvis.smart_home.tuya_adapter import TuyaAdapter


async def main() -> None:
    print("=" * 60)
    print(" JarvisAI - Tuya Device Discovery Test")
    print("=" * 60)

    adapter = TuyaAdapter()

    try:
        print()
        print("Connecting to Tuya Cloud...")

        await adapter.connect()

        print("Connected: PASS")

        print()
        print("Querying devices...")

        devices = await adapter.list_devices()

        print()
        print(f"Devices found: {len(devices)}")
        print()

        if not devices:
            print("No devices found.")
            return

        for index, device in enumerate(
            devices,
            start=1,
        ):
            print(f"[{index}]")
            print(f"ID       : {device.id}")
            print(f"Name     : {device.name}")
            print(f"Type     : {device.device_type}")
            print(f"Online   : {device.online}")
            print(f"Power    : {device.power}")
            print("-" * 40)

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