from __future__ import annotations

import asyncio

from jarvis.smart_home.tuya_adapter import TuyaAdapter


async def main() -> None:
    print("=" * 60)
    print(" JarvisAI - Tuya Cloud Authentication Test")
    print("=" * 60)

    adapter = TuyaAdapter()

    try:
        print()
        print("Connecting to Tuya Cloud...")

        await adapter.connect()

        print()
        print("Authentication: PASS")
        print(f"Connected     : {adapter.connected}")

        if not adapter.connected:
            raise RuntimeError(
                "TuyaAdapter did not enter connected state."
            )

        print()
        print(
            "Tuya Cloud authentication completed successfully."
        )

    except Exception as exc:
        print()
        print("Authentication: FAIL")
        print(
            f"Error         : "
            f"{type(exc).__name__}: {exc}"
        )
        raise

    finally:
        print()
        print("Disconnecting...")

        await adapter.disconnect()

        print(
            f"Connected     : {adapter.connected}"
        )

        print()
        print("=" * 60)
        print(" Test Complete")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())