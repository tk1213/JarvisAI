from __future__ import annotations

import asyncio

from jarvis.smart_home.tuya_adapter import TuyaAdapter


async def main() -> None:
    print("=" * 60)
    print(" JarvisAI - Tuya Device Status Test")
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

        print(f"Devices found: {len(devices)}")

        if not devices:
            print()
            print("No Tuya devices found.")
            return

        for index, device in enumerate(
            devices,
            start=1,
        ):
            print()
            print("-" * 60)
            print(f"Device #{index}")
            print("-" * 60)

            print(f"ID       : {device.id}")
            print(f"Name     : {device.name}")
            print(f"Type     : {device.device_type}")

            print()
            print("Reading raw Tuya status...")

            response = await adapter._request(
                method="GET",
                path=(
                    "/v1.0/iot-03/devices/"
                    f"{device.id}/status"
                ),
                access_token=adapter._access_token,
            )

            result = response.get("result")

            print()

            if not isinstance(result, list):
                print("Invalid status response.")
                print(f"Raw result: {result!r}")
                continue

            if not result:
                print("No status datapoints returned.")
                continue

            print("Status datapoints:")
            print()

            for item in result:
                if not isinstance(item, dict):
                    continue

                code = item.get("code")
                value = item.get("value")

                print(
                    f"  {code:<30} = {value!r}"
                )

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