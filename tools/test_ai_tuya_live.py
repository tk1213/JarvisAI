from __future__ import annotations

import asyncio

from jarvis.core.application import JarvisApplication
from jarvis.core.container import container
from jarvis.services.ai_capability_resolver import AICapabilityResolver
from jarvis.services.capability_router import CapabilityRouter
from jarvis.smart_home.service import SmartHomeService


async def execute_command(
    text: str,
    resolver: AICapabilityResolver,
    router: CapabilityRouter,
) -> None:
    print()
    print("-" * 60)
    print(f"User: {text}")

    request = await resolver.resolve(
        text,
    )

    if request is None:
        print("Capability: NONE")
        print("Action    : Normal AI fallback")
        return

    print(
        f"Capability: {request.capability}"
    )
    print(
        f"Arguments : {request.arguments}"
    )

    if (
        request.capability.startswith(
            "smart_home."
        )
        and "device_id" in request.arguments
    ):
        raise RuntimeError(
            "Safety check failed: "
            "AI generated device_id directly."
        )

    result = await router.execute_request(
        request,
    )

    print(
        f"Result    : {result}"
    )


async def show_devices(
    smart_home: SmartHomeService,
) -> None:
    devices = await smart_home.list_devices()

    print()
    print("=" * 60)
    print(" Current Tuya Device State")
    print("=" * 60)

    if not devices:
        print("No devices found.")
        return

    for device in devices:
        print(
            f"{device.name:<30} "
            f"type={device.device_type:<10} "
            f"online={device.online!s:<5} "
            f"power={device.power}"
        )


async def main() -> None:
    print("=" * 60)
    print(" JarvisAI - Live AI → Tuya Test")
    print("=" * 60)

    print()
    print(
        "WARNING: This test controls real Tuya devices."
    )

    app = JarvisApplication()

    try:
        await app.start(
            start_background_tasks=False,
        )

        resolver = container.resolve(
            "ai_capability_resolver",
            AICapabilityResolver,
        )

        router = container.resolve(
            "capability_router",
            CapabilityRouter,
        )

        smart_home = container.resolve(
            "smart_home",
            SmartHomeService,
        )

        await show_devices(
            smart_home
        )

        await execute_command(
            "เปิด Smart Plug",
            resolver,
            router,
        )

        await asyncio.sleep(2)

        await show_devices(
            smart_home
        )

        await execute_command(
            "ตรวจสอบสถานะ Smart Plug",
            resolver,
            router,
        )

        await execute_command(
            "ปิด Smart Plug",
            resolver,
            router,
        )

        await asyncio.sleep(2)

        await show_devices(
            smart_home
        )

        print()
        print("=" * 60)
        print(" Live AI → Tuya Test Complete")
        print("=" * 60)

    finally:
        await app.shutdown()


if __name__ == "__main__":
    asyncio.run(main())