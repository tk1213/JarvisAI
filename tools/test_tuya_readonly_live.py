from __future__ import annotations

import asyncio

from jarvis.smart_home.tuya_adapter import TuyaAdapter


async def main() -> None:
    print("Sprint 7 — Tuya Read-Only Live Gate")
    print("-" * 60)

    adapter = TuyaAdapter()

    try:
        print()
        print("Connecting to Tuya Cloud...")

        await adapter.connect()

        print("Connection: PASS")

        print()
        print("Discovering devices...")

        devices = await adapter.list_devices()

        print(
            f"Devices discovered: {len(devices)}"
        )

        for index, device in enumerate(
            devices,
            start=1,
        ):
            print()
            print(
                f"[{index}] {device.name}"
            )
            print(
                f"    ID       : {device.id}"
            )
            print(
                f"    Type     : {device.device_type}"
            )
            print(
                f"    Online   : {device.online}"
            )
            print(
                f"    Power    : {device.power}"
            )

        if not devices:
            raise RuntimeError(
                "Tuya connected successfully "
                "but no devices were discovered."
            )

        first_device = devices[0]

        print()
        print(
            "Reading status for first device..."
        )

        status = await adapter.get_status(
            first_device.id
        )

        print(
            f"Status records: {len(status)}"
        )

        for item in status:
            print(
                "    "
                f"{item.get('code')} = "
                f"{item.get('value')!r}"
            )

        print()
        print("Tuya read-only live gate: PASS")

    finally:
        print()
        print("Disconnecting...")

        await adapter.disconnect()

        print("Disconnected.")


if __name__ == "__main__":
    asyncio.run(
        main()
    )